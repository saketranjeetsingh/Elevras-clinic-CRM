import csv
import io
import re
from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi import UploadFile

from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import get_patient_for_current_user
from app.dependencies import require_permission
from app.models.appointment import Appointment
from app.models.bill import Bill
from app.models.patient import Patient
from app.models.treatment import Treatment
from app.models.doctor_profile import DoctorProfile
from app.models.user import User

from app.schemas.patient import PatientCreate
from app.schemas.patient import PatientResponse
from app.schemas.patient import PatientProfileResponse
from app.schemas.patient import PatientUpdate

from app.ratelimit import import_rate_limit


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

FIELD_ALIASES = {
    "name": {"name", "patientname", "fullname"},
    "phone": {"phone", "phonenumber", "mobile", "mobilenumber", "contactnumber"},
    "email": {"email", "emailaddress", "patientemail"},
    "date_of_birth": {"dateofbirth", "date_of_birth", "dob", "birthdate", "birth_date"},
    "age": {"age", "years"},
    "gender": {"gender", "sex"},
    "blood_group": {"bloodgroup", "blood_group", "bloodtype"},
    "medical_history": {"medicalhistory", "medical_history", "history"},
    "notes": {"notes", "remark", "remarks"},
    "last_treatment": {"lasttreatment", "last_treatment", "treatmentdate", "lastvisit"},
}


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").strip().lower())


def _coerce_patient_row(raw_row: dict, header_map: dict) -> dict:
    normalized = {}
    for field in [
        "name",
        "phone",
        "email",
        "date_of_birth",
        "gender",
        "blood_group",
        "medical_history",
        "notes",
        "last_treatment",
    ]:
        source_header = header_map.get(field)
        value = raw_row.get(source_header, "") if source_header else ""
        if isinstance(value, str):
            normalized[field] = value.strip()
        else:
            normalized[field] = value
    return normalized


def _validate_patient_row(row: dict) -> tuple[bool, list[str]]:
    errors = []

    name = str(row.get("name") or "").strip()
    if not name:
        errors.append("name is required")

    phone = str(row.get("phone") or "").strip()
    if not phone:
        errors.append("phone is required")
    elif len(phone) < 4:
        errors.append("phone is invalid")

    email = str(row.get("email") or "").strip()
    if email and ("@" not in email or "." not in email.split("@")[-1]):
        errors.append("email is invalid")

    dob_value = row.get("date_of_birth")
    if dob_value not in (None, ""):
        try:
            datetime.fromisoformat(str(dob_value).strip().replace("Z", "+00:00"))
        except (TypeError, ValueError):
            errors.append("date_of_birth must be a valid date (ISO format)")

    return not errors, errors


def _find_patient_duplicate(db: Session, organization_id: int, phone: str, email: str | None):
    contact_conditions = []
    if phone:
        contact_conditions.append(Patient.phone == phone)
    if email:
        contact_conditions.append(Patient.email == email)
    if not contact_conditions:
        return None
    return db.query(Patient).filter(
        Patient.organization_id == organization_id,
        or_(*contact_conditions)
    ).first()


def _parse_csv_preview(db: Session, organization_id: int, csv_text: str):
    if not csv_text or not csv_text.strip():
        return {
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "preview_rows": [],
            "duplicates": [],
            "mapped_columns": {},
            "unmapped_columns": [],
            "errors": [],
        }

    reader = csv.reader(io.StringIO(csv_text, newline=""))
    rows = list(reader)
    if not rows or not rows[0]:
        return {
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "preview_rows": [],
            "duplicates": [],
            "mapped_columns": {},
            "unmapped_columns": [],
            "errors": [],
        }

    header = rows[0]
    all_aliases = {alias for aliases in FIELD_ALIASES.values() for alias in aliases}
    header_map = {}
    for field, aliases in FIELD_ALIASES.items():
        for index, header_name in enumerate(header):
            if _normalize_header(header_name) in aliases:
                header_map[header_name] = field
                break

    unmapped_columns = [
        column for column in header
        if _normalize_header(column) not in all_aliases
    ]

    total_rows = len(rows) - 1
    valid_rows = 0
    invalid_rows = 0
    duplicates = []
    preview_rows = []
    errors = []

    for row_number, row in enumerate(rows[1:], start=1):
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))

        raw_row = {header[index]: row[index] if index < len(row) else "" for index in range(len(header))}
        patient_row = _coerce_patient_row(raw_row, {field: header for header, field in header_map.items()})

        if not any(str(value or "").strip() for value in patient_row.values()):
            errors.append({"row_number": row_number, "errors": ["empty row"]})
            invalid_rows += 1
            continue

        valid, validation_errors = _validate_patient_row(patient_row)
        if not valid:
            errors.append({"row_number": row_number, "errors": validation_errors})
            invalid_rows += 1
            continue

        phone = str(patient_row.get("phone") or "").strip()
        email = str(patient_row.get("email") or "").strip() or None
        duplicate = _find_patient_duplicate(db, organization_id, phone, email)
        if duplicate:
            duplicates.append({
                "row_number": row_number,
                "reason": "duplicate_phone_or_email",
                "duplicate_id": duplicate.id,
            })

        age_value = patient_row.get("age")
        if age_value not in (None, ""):
            patient_row["age"] = int(str(age_value).strip())

        preview_rows.append(patient_row)
        valid_rows += 1

    return {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "preview_rows": preview_rows,
        "duplicates": duplicates,
        "mapped_columns": header_map,
        "unmapped_columns": unmapped_columns,
        "errors": errors,
    }


@router.post("/import/preview")
def preview_patient_import(
    file: UploadFile = File(...),
    _: None = Depends(import_rate_limit),
    current_user: User = Depends(get_current_user_with_org),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)
    content = file.file.read()
    csv_text = content.decode("utf-8-sig") if isinstance(content, bytes) else str(content)
    return _parse_csv_preview(db, org_id, csv_text)


@router.post("/import/confirm")
def confirm_patient_import(
    payload: dict,
    _: None = Depends(import_rate_limit),
    current_user: User = Depends(get_current_user_with_org),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)
    rows = payload.get("rows", []) if isinstance(payload, dict) else []
    imported_count = 0
    skipped_duplicates = 0
    failed_validation = 0

    for row in rows:
        if not isinstance(row, dict):
            failed_validation += 1
            continue

        patient_row = {
            "name": str(row.get("name") or "").strip(),
            "phone": str(row.get("phone") or "").strip(),
            "email": str(row.get("email") or "").strip() or None,
            "date_of_birth": row.get("date_of_birth"),
            "gender": str(row.get("gender") or "").strip() or None,
            "blood_group": str(row.get("blood_group") or "").strip() or None,
            "medical_history": str(row.get("medical_history") or "").strip() or None,
            "notes": str(row.get("notes") or "").strip() or None,
            "last_treatment": str(row.get("last_treatment") or "").strip() or None,
        }

        valid, validation_errors = _validate_patient_row(patient_row)
        if not valid:
            failed_validation += 1
            continue

        duplicate = _find_patient_duplicate(
            db,
            org_id,
            patient_row["phone"],
            patient_row["email"],
        )
        if duplicate:
            skipped_duplicates += 1
            continue

        dob_value = patient_row.get("date_of_birth")
        if dob_value not in (None, ""):
            try:
                patient_row["date_of_birth"] = datetime.fromisoformat(str(dob_value).strip().replace("Z", "+00:00"))
            except (TypeError, ValueError):
                failed_validation += 1
                continue
        else:
            patient_row["date_of_birth"] = None

        new_patient = Patient(
            organization_id=org_id,
            name=patient_row["name"],
            phone=patient_row["phone"],
            email=patient_row["email"],
            date_of_birth=patient_row.get("date_of_birth"),
            gender=patient_row.get("gender"),
            blood_group=patient_row.get("blood_group"),
            medical_history=patient_row.get("medical_history"),
            notes=patient_row.get("notes"),
            last_treatment=patient_row.get("last_treatment"),
        )
        db.add(new_patient)
        imported_count += 1

    db.commit()
    return {
        "imported_count": imported_count,
        "skipped_duplicates": skipped_duplicates,
        "failed_validation": failed_validation,
    }


@router.post("", response_model=PatientResponse)
@router.post("/", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    current_user: User = Depends(require_permission("patient:create")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    existing_patient = _find_patient_duplicate(
        db,
        org_id,
        patient.phone,
        patient.email,
    )

    if existing_patient:
        raise HTTPException(
            status_code=409,
            detail="Patient already exists"
        )

    new_patient = Patient(
        organization_id=org_id,
        name=patient.name,
        phone=patient.phone,
        email=patient.email,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        blood_group=patient.blood_group,
        medical_history=patient.medical_history,
        notes=patient.notes,
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


@router.get("", response_model=list[PatientResponse])
@router.get("/", response_model=list[PatientResponse])
def get_patients(
    current_user: User = Depends(require_permission("patient:view")),
    db: Session = Depends(get_db),
    request: Request = None,
    skip: int = Query(0, ge=0),
    limit: int | None = Query(None, ge=1, le=500),
):
    org_id = get_organization_id(request)

    query = db.query(Patient).filter(
        Patient.organization_id == org_id
    ).order_by(Patient.id.desc())

    patients = query.offset(skip).limit(limit).all() if limit else query.all()

    patient_ids = [patient.id for patient in patients]

    latest_treatment_names = {}
    if patient_ids:
        ranked = (
            db.query(
                Treatment.patient_id,
                Treatment.id,
                func.row_number().over(
                    partition_by=Treatment.patient_id,
                    order_by=(
                        Treatment.treatment_date.desc().nullslast(),
                        Treatment.id.desc(),
                    ),
                ).label("rn"),
            )
            .filter(
                Treatment.patient_id.in_(patient_ids),
                Treatment.organization_id == org_id,
            )
            .subquery()
        )

        latest_rows = (
            db.query(ranked.c.patient_id, ranked.c.id)
            .filter(ranked.c.rn == 1)
            .all()
        )

        treatment_ids = [row.id for row in latest_rows]
        name_by_id = {}
        if treatment_ids:
            name_by_id = dict(
                db.query(Treatment.id, Treatment.treatment_name).filter(
                    Treatment.id.in_(treatment_ids)
                ).all()
            )

        latest_treatment_names = {
            row.patient_id: name_by_id[row.id]
            for row in latest_rows
            if row.id in name_by_id
        }

    for patient in patients:
        patient.last_treatment = latest_treatment_names.get(patient.id)

    return patients


@router.get("/{patient_id}/profile")
def get_patient_profile(
    patient_id: int,
    current_user: User = Depends(require_permission("patient:view")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.organization_id == org_id
    ).all()

    treatments = db.query(Treatment).filter(
        Treatment.patient_id == patient_id,
        Treatment.organization_id == org_id
    ).all()

    bills = db.query(Bill).filter(
        Bill.patient_id == patient_id,
        Bill.organization_id == org_id
    ).all()

    doctor_ids = {treatment.doctor_id for treatment in treatments if treatment.doctor_id is not None}
    doctors = db.query(DoctorProfile).filter(DoctorProfile.id.in_(doctor_ids)).all() if doctor_ids else []
    doctor_map = {doctor.id: doctor.name for doctor in doctors}

    normalized_treatments = []
    for treatment in treatments:
        normalized_treatments.append({
            "id": treatment.id,
            "patient_id": treatment.patient_id,
            "treatment_name": treatment.treatment_name,
            "cost": treatment.cost,
            "status": treatment.status,
            "notes": treatment.notes,
            "treatment_date": treatment.treatment_date,
            "doctor_name": doctor_map.get(treatment.doctor_id, "Unknown Doctor"),
        })

    pending_amount = sum(
        bill.amount or 0 for bill in bills
        if (bill.payment_status or "").lower() != "paid"
    )

    latest_treatment_name = patient.last_treatment
    if treatments:
        dated_treatments = [
            treatment for treatment in treatments if treatment.treatment_date is not None
        ]
        latest_treatment = max(
            dated_treatments or treatments,
            key=lambda treatment: (
                treatment.treatment_date or datetime.min.replace(tzinfo=timezone.utc)
            ),
        )
        latest_treatment_name = latest_treatment.treatment_name
        patient.last_treatment = latest_treatment_name

    return {
        "patient": patient,
        "appointments": appointments,
        "treatments": normalized_treatments,
        "bills": bills,
        "stats": {
            "appointments": len(appointments),
            "treatments": len(treatments),
            "bills": len(bills),
            "pending_amount": pending_amount,
            "last_treatment": latest_treatment_name,
        },
    }


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient: Patient = Depends(get_patient_for_current_user),
):
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    updated_patient: PatientUpdate,
    current_user: User = Depends(require_permission("patient:edit")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if updated_patient.name is not None:
        patient.name = updated_patient.name

    if updated_patient.phone is not None:
        duplicate_phone = db.query(Patient).filter(
            Patient.organization_id == org_id,
            Patient.id != patient_id,
            Patient.phone == updated_patient.phone
        ).first()

        if duplicate_phone:
            raise HTTPException(
                status_code=409,
                detail="Patient already exists"
            )

        patient.phone = updated_patient.phone

    if updated_patient.email is not None:
        duplicate_email = db.query(Patient).filter(
            Patient.organization_id == org_id,
            Patient.id != patient_id,
            Patient.email == updated_patient.email
        ).first()

        if duplicate_email:
            raise HTTPException(
                status_code=409,
                detail="Patient already exists"
            )

        patient.email = updated_patient.email

    if updated_patient.date_of_birth is not None:
        patient.date_of_birth = updated_patient.date_of_birth

    if updated_patient.gender is not None:
        patient.gender = updated_patient.gender

    if updated_patient.blood_group is not None:
        patient.blood_group = updated_patient.blood_group

    if updated_patient.medical_history is not None:
        patient.medical_history = updated_patient.medical_history

    if updated_patient.notes is not None:
        patient.notes = updated_patient.notes

    db.commit()
    db.refresh(patient)

    return patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    current_user: User = Depends(require_permission("patient:delete")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    appointment_count = db.query(Appointment.id).filter(
        Appointment.patient_id == patient_id,
        Appointment.organization_id == org_id,
    ).count()
    treatment_count = db.query(Treatment.id).filter(
        Treatment.patient_id == patient_id,
        Treatment.organization_id == org_id,
    ).count()
    bill_count = db.query(Bill.id).filter(
        Bill.patient_id == patient_id,
        Bill.organization_id == org_id,
    ).count()

    if appointment_count or treatment_count or bill_count:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete patient with existing appointments, treatments, or bills.",
        )

    db.delete(patient)
    db.commit()

    return {
        "message": "Patient deleted successfully"
    }