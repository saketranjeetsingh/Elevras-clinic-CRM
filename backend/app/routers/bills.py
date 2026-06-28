from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.bill import Bill
from app.schemas.bill import BillCreate

from app.dependencies import get_current_doctor


router = APIRouter(
    prefix="/bills",
    tags=["Bills"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/")
def create_bill(
    bill: BillCreate,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    new_bill = Bill(
        doctor_id=current_doctor["doctor_id"],
        patient_id=bill.patient_id,
        amount=bill.amount,
        payment_status=bill.payment_status,
        payment_method=bill.payment_method
    )

    db.add(new_bill)

    db.commit()

    db.refresh(new_bill)

    return new_bill


@router.get("/")
def get_bills(
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    return db.query(Bill).filter(
        Bill.doctor_id ==
        current_doctor["doctor_id"]
    ).all()


@router.put("/{bill_id}")
def update_bill_status(
    bill_id: int,
    payment_status: str,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.doctor_id == current_doctor["doctor_id"]
    ).first()

    if not bill:
        return {
            "message": "Bill not found"
        }

    bill.payment_status = payment_status

    db.commit()

    db.refresh(bill)

    return bill