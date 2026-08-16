from datetime import datetime

from pydantic import BaseModel


class TreatmentCreate(BaseModel):

    patient_id: int
    treatment_name: str
    cost: int
    status: str
    notes: str | None = None
    treatment_date: datetime | None = None


class TreatmentUpdate(BaseModel):
    patient_id: int | None = None
    treatment_name: str | None = None
    cost: int | None = None
    status: str | None = None
    notes: str | None = None
    treatment_date: datetime | None = None


class TreatmentResponse(BaseModel):

    id: int
    patient_id: int
    treatment_name: str
    cost: int
    status: str
    notes: str | None = None
    treatment_date: datetime | None = None

    class Config:
        from_attributes = True