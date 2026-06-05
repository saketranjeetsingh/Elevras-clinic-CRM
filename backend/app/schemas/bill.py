from pydantic import BaseModel


class BillCreate(BaseModel):

    patient_id: int
    amount: int
    payment_status: str
    payment_method: str


class BillResponse(BaseModel):

    id: int
    patient_id: int
    amount: int
    payment_status: str
    payment_method: str

    class Config:
        from_attributes = True