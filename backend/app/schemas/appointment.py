from datetime import datetime

from pydantic import BaseModel
from pydantic import validator

from app.constants import AppointmentStatus
from app.constants import normalize_status


def _validate_appointment_date(value):

    if value is None:
        return None

    if not isinstance(value, str) or not value.strip():
        raise ValueError("appointment_date must be a valid date (YYYY-MM-DD)")

    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
    except ValueError:
        raise ValueError("appointment_date must be in YYYY-MM-DD format")

    return value.strip()


class AppointmentCreate(BaseModel):

    patient_id: int

    doctor_name: str

    appointment_date: str

    status: AppointmentStatus

    notes: str | None = None

    _normalize_status = validator(
        "status",
        pre=True,
        allow_reuse=True,
    )(normalize_status)

    _validate_date = validator(
        "appointment_date",
        allow_reuse=True,
    )(_validate_appointment_date)


class AppointmentUpdate(BaseModel):

    patient_id: int | None = None

    doctor_name: str | None = None

    appointment_date: str | None = None

    status: AppointmentStatus | None = None

    notes: str | None = None

    _normalize_status = validator(
        "status",
        pre=True,
        allow_reuse=True,
    )(normalize_status)

    _validate_date = validator(
        "appointment_date",
        allow_reuse=True,
    )(_validate_appointment_date)


class AppointmentResponse(BaseModel):

    id: int

    patient_id: int

    doctor_name: str

    appointment_date: str

    status: str

    notes: str | None = None

    class Config:
        orm_mode = True
