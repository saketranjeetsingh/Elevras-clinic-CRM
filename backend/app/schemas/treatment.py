from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from app.constants import TreatmentStatus
from app.constants import normalize_status


class TreatmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    treatment_name: str
    cost: int = Field(ge=0, le=100000000)
    status: TreatmentStatus
    notes: Optional[str] = None
    treatment_date: Optional[datetime] = None

    @validator("status", pre=True, allow_reuse=True)
    def _normalize_status(cls, v):
        return normalize_status(v)


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    treatment_name: Optional[str] = None
    cost: Optional[int] = Field(None, ge=0, le=100000000)
    status: Optional[TreatmentStatus] = None
    notes: Optional[str] = None
    treatment_date: Optional[datetime] = None

    @validator("status", pre=True, allow_reuse=True)
    def _normalize_status(cls, v):
        return normalize_status(v)


class TreatmentResponse(BaseModel):
    id: int
    organization_id: int
    patient_id: int
    doctor_id: int
    treatment_name: str
    cost: int
    status: str
    notes: Optional[str] = None
    treatment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True