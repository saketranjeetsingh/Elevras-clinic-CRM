from pydantic import BaseModel


class AppointmentCreate(BaseModel):

    patient_id: int

    doctor_name: str

    appointment_date: str

    status: str

    notes: str


class AppointmentResponse(AppointmentCreate):

    id: int

    class Config:
        from_attributes = True