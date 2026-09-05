from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from app.constants import BillPaymentStatus
from app.constants import normalize_status


class BillBase(BaseModel):
    patient_id: int
    doctor_id: int
    amount: int = Field(ge=0, le=100000000)
    payment_status: BillPaymentStatus
    payment_method: Optional[str] = None

    @validator("payment_status", pre=True, allow_reuse=True)
    def _normalize_status(cls, v):
        return normalize_status(v)


class BillCreate(BillBase):
    pass


class BillUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    amount: Optional[int] = Field(None, ge=0, le=100000000)
    payment_status: Optional[BillPaymentStatus] = None
    payment_method: Optional[str] = None

    @validator("payment_status", pre=True, allow_reuse=True)
    def _normalize_status(cls, v):
        return normalize_status(v)


class BillResponse(BaseModel):
    id: int
    organization_id: int
    patient_id: int
    doctor_id: int
    amount: int
    payment_status: str
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True