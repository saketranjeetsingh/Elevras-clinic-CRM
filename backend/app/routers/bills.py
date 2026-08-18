from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.bill import Bill
from app.schemas.bill import BillCreate
from app.schemas.bill import BillResponse
from app.schemas.bill import BillUpdate

from app.dependencies import get_current_doctor
from app.dependencies import get_patient_for_current_doctor


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


@router.post("", response_model=BillResponse)
@router.post("/", response_model=BillResponse)
def create_bill(
    bill: BillCreate,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    get_patient_for_current_doctor(
        bill.patient_id,
        current_doctor,
        db
    )

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


@router.get("", response_model=list[BillResponse])
@router.get("/", response_model=list[BillResponse])
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


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_data: BillUpdate,
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
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    if bill_data.patient_id is not None:
        get_patient_for_current_doctor(bill_data.patient_id, current_doctor, db)
        bill.patient_id = bill_data.patient_id

    if bill_data.amount is not None:
        bill.amount = bill_data.amount

    if bill_data.payment_status is not None:
        bill.payment_status = bill_data.payment_status

    if bill_data.payment_method is not None:
        bill.payment_method = bill_data.payment_method

    db.commit()

    db.refresh(bill)

    return bill


@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.doctor_id == current_doctor["doctor_id"],
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    db.delete(bill)
    db.commit()

    return {"message": "Bill deleted successfully"}