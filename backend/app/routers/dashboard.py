from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.models.bill import Bill
from app.models.user import User


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(require_permission("dashboard:view")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    total_patients = db.query(Patient).filter(
        Patient.organization_id == org_id
    ).count()

    total_appointments = db.query(Appointment).filter(
        Appointment.organization_id == org_id
    ).count()

    total_treatments = db.query(Treatment).filter(
        Treatment.organization_id == org_id
    ).count()

    total_bills = db.query(Bill).filter(
        Bill.organization_id == org_id
    ).count()

    paid_bills = db.query(Bill).filter(
        Bill.organization_id == org_id,
        func.lower(Bill.payment_status) == "paid"
    ).all()

    pending_bills = db.query(Bill).filter(
        Bill.organization_id == org_id,
        func.lower(Bill.payment_status) != "paid"
    ).all()

    total_revenue = sum(bill.amount or 0 for bill in paid_bills)
    pending_revenue = sum(bill.amount or 0 for bill in pending_bills)

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "total_treatments": total_treatments,
        "total_bills": total_bills,
        "paid_bills": len(paid_bills),
        "pending_bills": len(pending_bills),
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
    }