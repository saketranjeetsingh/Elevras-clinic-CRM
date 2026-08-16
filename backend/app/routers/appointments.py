from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate
from app.schemas.appointment import AppointmentUpdate
from app.dependencies import get_current_doctor
from app.dependencies import get_patient_for_current_doctor


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


@router.post("")
@router.post("/")
def create_appointment(
    appointment: AppointmentCreate,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    get_patient_for_current_doctor(
        appointment.patient_id,
        current_doctor,
        db
    )

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


@router.get("")
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
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
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
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    if appointment_data.patient_id is not None:
        get_patient_for_current_doctor(appointment_data.patient_id, current_doctor, db)
        appointment.patient_id = appointment_data.patient_id

    if appointment_data.doctor_name is not None:
        appointment.doctor_name = appointment_data.doctor_name

    if appointment_data.appointment_date is not None:
        appointment.appointment_date = appointment_data.appointment_date

    if appointment_data.status is not None:
        appointment.status = appointment_data.status

    if appointment_data.notes is not None:
        appointment.notes = appointment_data.notes

    db.commit()

    db.refresh(appointment)

    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id == current_doctor["doctor_id"],
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment deleted successfully"}