from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.bill import Bill
from app.models.patient import Patient
from app.models.user import User

from app.schemas.bill import BillCreate
from app.schemas.bill import BillResponse
from app.schemas.bill import BillUpdate

from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission


router = APIRouter(
    prefix="/bills",
    tags=["Bills"]
)


@router.post("", response_model=BillResponse)
@router.post("/", response_model=BillResponse)
def create_bill(
    bill: BillCreate,
    current_user: User = Depends(require_permission("bill:create")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == bill.patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    new_bill = Bill(
        organization_id=org_id,
        patient_id=bill.patient_id,
        doctor_id=bill.doctor_id,
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
    current_user: User = Depends(require_permission("bill:view")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    return db.query(Bill).filter(
        Bill.organization_id == org_id
    ).all()


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_data: BillUpdate,
    current_user: User = Depends(require_permission("bill:edit")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.organization_id == org_id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    if bill_data.patient_id is not None:
        patient = db.query(Patient).filter(
            Patient.id == bill_data.patient_id,
            Patient.organization_id == org_id
        ).first()
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        bill.patient_id = bill_data.patient_id

    if bill_data.doctor_id is not None:
        bill.doctor_id = bill_data.doctor_id

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
    current_user: User = Depends(require_permission("bill:delete")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.organization_id == org_id,
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    db.delete(bill)
    db.commit()

    return {"message": "Bill deleted successfully"}