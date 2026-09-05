from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.appointment import AppointmentResponse
from app.schemas.bill import BillResponse


class PatientBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None


class PatientResponse(PatientBase):
    id: int
    organization_id: int
    doctor_id: Optional[int] = None
    last_treatment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TreatmentProfileItem(BaseModel):
    id: int
    patient_id: int
    treatment_name: str
    cost: Optional[int] = None
    status: str
    notes: Optional[str] = None
    treatment_date: Optional[datetime] = None
    doctor_name: str = "Unknown Doctor"


class PatientProfileResponse(BaseModel):
    patient: PatientResponse
    appointments: list["AppointmentResponse"]
    treatments: list["TreatmentProfileItem"]
    bills: list["BillResponse"]
    stats: dict

    class Config:
        orm_mode = True
