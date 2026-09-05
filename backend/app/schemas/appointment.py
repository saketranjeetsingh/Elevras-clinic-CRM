from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import validator

from app.constants import AppointmentStatus
from app.constants import normalize_status


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    doctor_name: Optional[str] = None
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    notes: Optional[str] = None

    @validator("status", pre=True, allow_reuse=True)
    def _normalize_status(cls, v):
        return normalize_status(v)


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    doctor_name: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

    @validator("status", pre=True, allow_reuse=True)
    def _normalize_status(cls, v):
        return normalize_status(v)


class AppointmentResponse(BaseModel):
    id: int
    organization_id: int
    patient_id: int
    doctor_id: int
    doctor_name: Optional[str] = None
    start_at: datetime
    end_at: datetime
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True