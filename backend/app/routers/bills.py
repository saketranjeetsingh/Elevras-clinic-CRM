from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.bill import Bill
from app.schemas.bill import BillCreate


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
    db: Session = Depends(get_db)
):

    new_bill = Bill(
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
    db: Session = Depends(get_db)
):

    return db.query(Bill).all()