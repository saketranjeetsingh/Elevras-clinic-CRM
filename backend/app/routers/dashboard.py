from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal

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
    db: Session = Depends(get_db)
):

    total_patients = db.query(Patient).count()

    total_appointments = db.query(Appointment).count()

    total_treatments = db.query(Treatment).count()

    total_bills = db.query(Bill).count()

    total_revenue = db.query(
        func.sum(Bill.amount)
    ).scalar()

    if total_revenue is None:
        total_revenue = 0

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "total_treatments": total_treatments,
        "total_bills": total_bills,
        "total_revenue": total_revenue
    }