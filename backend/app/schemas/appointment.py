from pydantic import BaseModel


class AppointmentCreate(BaseModel):

    patient_id: int

    doctor_name: str

    appointment_date: str

    status: str

    notes: str | None = None


class AppointmentUpdate(BaseModel):
    patient_id: int | None = None
    doctor_name: str | None = None
    appointment_date: str | None = None
    status: str | None = None
    notes: str | None = None


class AppointmentResponse(AppointmentCreate):

    id: int

    class Config:
        from_attributes = True