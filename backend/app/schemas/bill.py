from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from app.constants import BillPaymentStatus
from app.constants import normalize_status


class BillCreate(BaseModel):

    patient_id: int

    amount: int = Field(ge=0, le=100000000)

    payment_status: BillPaymentStatus

    payment_method: str | None = None

    _normalize_status = validator(
        "payment_status",
        pre=True,
        allow_reuse=True,
    )(normalize_status)


class BillUpdate(BaseModel):

    patient_id: int | None = None

    amount: int | None = Field(None, ge=0, le=100000000)

    payment_status: BillPaymentStatus | None = None

    payment_method: str | None = None

    _normalize_status = validator(
        "payment_status",
        pre=True,
        allow_reuse=True,
    )(normalize_status)


class BillResponse(BaseModel):

    id: int

    patient_id: int

    amount: int

    payment_status: str

    payment_method: str | None = None

    class Config:
        orm_mode = True
