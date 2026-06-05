from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.doctor import Doctor

from app.schemas.doctor import DoctorSignup
from app.schemas.doctor import DoctorLogin

from app.security import hash_password
from app.security import verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/signup")
def signup(
    doctor: DoctorSignup,
    db: Session = Depends(get_db)
):

    existing_doctor = db.query(Doctor).filter(
        Doctor.email == doctor.email
    ).first()

    if existing_doctor:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_doctor = Doctor(
        name=doctor.name,
        email=doctor.email,
        hashed_password=hash_password(
            doctor.password
        ),
        clinic_name=doctor.clinic_name
    )

    db.add(new_doctor)

    db.commit()

    db.refresh(new_doctor)

    return {
        "message": "Doctor created successfully"
    }


@router.post("/login")
def login(
    doctor: DoctorLogin,
    db: Session = Depends(get_db)
):

    db_doctor = db.query(Doctor).filter(
        Doctor.email == doctor.email
    ).first()

    if not db_doctor:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        doctor.password,
        db_doctor.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return {
        "message": "Login successful",
        "doctor_id": db_doctor.id
    }