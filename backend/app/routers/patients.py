from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.dependencies import get_current_doctor
from app.database import SessionLocal
from app.models.patient import Patient
from app.models.treatment import Treatment

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


@router.post("/")
def create_patient(
    patient: PatientCreate,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    new_patient = Patient(
        doctor_id=current_doctor["doctor_id"],
        name=patient.name,
        phone=patient.phone,
        email=patient.email,
        age=patient.age,
        gender=patient.gender,
        notes=patient.notes,
        last_treatment=patient.last_treatment
    )

    db.add(new_patient)

    db.commit()

    db.refresh(new_patient)

    return new_patient


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
    db: Session = Depends(get_db)
):

    treatments = db.query(Treatment).filter(
        Treatment.patient_id == patient_id
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
        patient.phone = updated_patient.phone

    if updated_patient.email is not None:
        patient.email = updated_patient.email

    if updated_patient.age is not None:
        patient.age = updated_patient.age

    if updated_patient.gender is not None:
        patient.gender = updated_patient.gender

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

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

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