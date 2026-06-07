from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate
from app.dependencies import get_current_doctor


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/")
def create_appointment(
    appointment: AppointmentCreate,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    new_appointment = Appointment(
        doctor_id=current_doctor["doctor_id"],
        patient_id=appointment.patient_id,
        doctor_name=appointment.doctor_name,
        appointment_date=appointment.appointment_date,
        status=appointment.status,
        notes=appointment.notes
    )

    db.add(new_appointment)

    db.commit()

    db.refresh(new_appointment)

    return new_appointment


@router.get("/")
def get_appointments(
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    return db.query(Appointment).filter(
        Appointment.doctor_id ==
        current_doctor["doctor_id"]
    ).all()


@router.put("/{appointment_id}")
def update_appointment_status(
    appointment_id: int,
    status: str,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id ==
        current_doctor["doctor_id"]
    ).first()

    if not appointment:
        return {
            "message": "Appointment not found"
        }

    appointment.status = status

    db.commit()

    db.refresh(appointment)

    return appointment