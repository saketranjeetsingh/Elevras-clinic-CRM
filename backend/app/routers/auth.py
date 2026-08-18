from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.doctor import Doctor

from app.schemas.doctor import DoctorSignup

from app.dependencies import get_current_doctor

from app.security import hash_password
from app.security import verify_password
from app.security import create_access_token

from app.ratelimit import auth_rate_limit


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
    _: None = Depends(auth_rate_limit),
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
    form_data: OAuth2PasswordRequestForm = Depends(),
    _: None = Depends(auth_rate_limit),
    db: Session = Depends(get_db)
):

    email = form_data.username
    password = form_data.password

    if not email or not password:
        raise HTTPException(
            status_code=422,
            detail="Validation failed"
        )

    db_doctor = db.query(Doctor).filter(
        Doctor.email == email
    ).first()

    if not db_doctor:
        raise HTTPException(
            status_code=401,
            detail="Invalid email"
        )

    if not verify_password(
        password,
        db_doctor.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        {
            "doctor_id": db_doctor.id,
            "email": db_doctor.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_me(
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    db_doctor = db.query(Doctor).filter(
        Doctor.id == current_doctor["doctor_id"]
    ).first()

    if not db_doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return {
        "doctor_id": db_doctor.id,
        "doctor_name": db_doctor.name,
        "clinic_name": db_doctor.clinic_name,
        "email": db_doctor.email
    }
