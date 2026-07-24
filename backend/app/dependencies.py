from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.security import verify_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_doctor(
    token: str = Depends(oauth2_scheme)
):

    payload = verify_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return payload


def get_patient_for_current_doctor(
    patient_id: int,
    current_doctor: dict,
    db: Session
):

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if patient.doctor_id != current_doctor["doctor_id"]:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to create records for this patient"
        )

    return patient