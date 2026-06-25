from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.dependencies import get_current_doctor

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.models.bill import Bill


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/stats")
def get_dashboard_stats(
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    doctor_id = current_doctor["doctor_id"]

    total_patients = db.query(Patient).filter(
        Patient.doctor_id == doctor_id
    ).count()

    total_appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).count()

    total_treatments = db.query(Treatment).filter(
        Treatment.doctor_id == doctor_id
    ).count()

    total_bills = db.query(Bill).filter(
        Bill.doctor_id == doctor_id
    ).count()

    total_revenue = db.query(
        func.sum(Bill.amount)
    ).filter(Bill.doctor_id == doctor_id).scalar()

    if total_revenue is None:
        total_revenue = 0

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "total_treatments": total_treatments,
        "total_bills": total_bills,
        "total_revenue": total_revenue
    }