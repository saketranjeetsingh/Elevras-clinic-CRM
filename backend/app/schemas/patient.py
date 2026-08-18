from datetime import datetime

from pydantic import BaseModel

from app.schemas.appointment import AppointmentResponse
from app.schemas.bill import BillResponse


class PatientCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None
    age: int | None = None
    gender: str | None = None
    blood_group: str | None = None
    medical_history: str | None = None
    notes: str | None = None


class PatientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    age: int | None = None
    gender: str | None = None
    blood_group: str | None = None
    medical_history: str | None = None
    notes: str | None = None


class PatientResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None = None
    age: int | None = None
    gender: str | None = None
    blood_group: str | None = None
    medical_history: str | None = None
    notes: str | None = None
    last_treatment: str | None = None

    class Config:
        orm_mode = True


class TreatmentProfileItem(BaseModel):
    id: int
    patient_id: int
    treatment_name: str
    cost: int | None = None
    status: str
    notes: str | None = None
    treatment_date: datetime | None = None
    doctor_name: str = "Unknown Doctor"


class PatientProfileResponse(BaseModel):
    patient: PatientResponse
    appointments: list[AppointmentResponse]
    treatments: list[TreatmentProfileItem]
    bills: list[BillResponse]
    stats: dict
