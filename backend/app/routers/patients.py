from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.dependencies import get_current_doctor
from app.database import SessionLocal
from app.models.appointment import Appointment
from app.models.bill import Bill
from app.models.patient import Patient
from app.models.treatment import Treatment
from app.models.doctor import Doctor

from app.schemas.patient import PatientCreate
from app.schemas.patient import PatientUpdate


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("")
@router.post("/")
def create_patient(
    patient: PatientCreate,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    existing_patient = db.query(Patient).filter(
        Patient.doctor_id == current_doctor["doctor_id"],
        or_(Patient.phone == patient.phone, Patient.email == patient.email)
    ).first()

    if existing_patient:
        raise HTTPException(
            status_code=409,
            detail="Patient already exists"
        )

    new_patient = Patient(
        doctor_id=current_doctor["doctor_id"],
        name=patient.name,
        phone=patient.phone,
        email=patient.email,
        age=patient.age,
        gender=patient.gender,
        address=patient.address,
        blood_group=patient.blood_group,
        medical_history=patient.medical_history,
        notes=patient.notes,
        last_treatment=patient.last_treatment
    )

    db.add(new_patient)

    db.commit()

    db.refresh(new_patient)

    return new_patient


@router.get("")
@router.get("/")
def get_patients(
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    return db.query(Patient).filter(
        Patient.doctor_id == current_doctor["doctor_id"]
    ).all()


@router.get("/{patient_id}/treatments")
def get_patient_treatments(
    patient_id: int,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    treatments = db.query(Treatment).filter(
        Treatment.patient_id == patient_id,
        Treatment.doctor_id == current_doctor["doctor_id"]
    ).all()

    return treatments


@router.get("/search")
def search_patient(
    phone: str,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    patient = db.query(Patient).filter(
        Patient.phone == phone,
        Patient.doctor_id == current_doctor["doctor_id"]
    ).first()

    return patient


@router.get("/{patient_id}/profile")
def get_patient_profile(
    patient_id: int,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == current_doctor["doctor_id"]
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.doctor_id == current_doctor["doctor_id"]
    ).all()

    treatments = db.query(Treatment).filter(
        Treatment.patient_id == patient_id,
        Treatment.doctor_id == current_doctor["doctor_id"]
    ).all()

    bills = db.query(Bill).filter(
        Bill.patient_id == patient_id,
        Bill.doctor_id == current_doctor["doctor_id"]
    ).all()

    doctor_ids = {treatment.doctor_id for treatment in treatments if treatment.doctor_id is not None}
    doctors = db.query(Doctor).filter(Doctor.id.in_(doctor_ids)).all() if doctor_ids else []
    doctor_map = {doctor.id: doctor.name for doctor in doctors}

    normalized_treatments = []
    for treatment in treatments:
        normalized_treatments.append({
            **treatment.__dict__,
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


@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == current_doctor["doctor_id"]
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.put("/{patient_id}")
def update_patient(
    patient_id: int,
    updated_patient: PatientUpdate,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == current_doctor["doctor_id"]
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
            Patient.doctor_id == current_doctor["doctor_id"],
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
            Patient.doctor_id == current_doctor["doctor_id"],
            Patient.id != patient_id,
            Patient.email == updated_patient.email
        ).first()

        if duplicate_email:
            raise HTTPException(
                status_code=409,
                detail="Patient already exists"
            )

        patient.email = updated_patient.email

    if updated_patient.age is not None:
        patient.age = updated_patient.age

    if updated_patient.gender is not None:
        patient.gender = updated_patient.gender

    if updated_patient.address is not None:
        patient.address = updated_patient.address

    if updated_patient.blood_group is not None:
        patient.blood_group = updated_patient.blood_group

    if updated_patient.medical_history is not None:
        patient.medical_history = updated_patient.medical_history

    if updated_patient.notes is not None:
        patient.notes = updated_patient.notes

    if updated_patient.last_treatment is not None:
        patient.last_treatment = updated_patient.last_treatment

    db.commit()
    db.refresh(patient)

    return patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == current_doctor["doctor_id"]
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).delete(synchronize_session=False)

    db.query(Treatment).filter(
        Treatment.patient_id == patient_id
    ).delete(synchronize_session=False)

    db.query(Bill).filter(
        Bill.patient_id == patient_id
    ).delete(synchronize_session=False)

    db.delete(patient)
    db.commit()

    return {
        "message": "Patient deleted successfully"
    }


@router.get("/search/phone/{phone}")
def search_patient_by_phone(
    phone: str,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    patient = db.query(Patient).filter(
        Patient.phone == phone,
        Patient.doctor_id == current_doctor["doctor_id"]
    ).first()

    return patient


@router.get("/search/name/{name}")
def search_patient_by_name(
    name: str,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    patients = db.query(Patient).filter(
        Patient.name.ilike(f"%{name}%"),
        Patient.doctor_id == current_doctor["doctor_id"]
    ).all()

    return patients