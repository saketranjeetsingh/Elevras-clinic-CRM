from pydantic import BaseModel


class BillCreate(BaseModel):

    patient_id: int
    amount: int
    payment_status: str
    payment_method: str | None = None


class BillUpdate(BaseModel):
    patient_id: int | None = None
    amount: int | None = None
    payment_status: str | None = None
    payment_method: str | None = None


class BillResponse(BaseModel):

    id: int
    patient_id: int
    amount: int
    payment_status: str
    payment_method: str | None = None

    class Config:
        from_attributes = True