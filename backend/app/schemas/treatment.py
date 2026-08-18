from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from app.constants import TreatmentStatus
from app.constants import normalize_status


class TreatmentCreate(BaseModel):

    patient_id: int

    treatment_name: str

    cost: int = Field(ge=0, le=100000000)

    status: TreatmentStatus

    notes: str | None = None

    treatment_date: datetime | None = None

    _normalize_status = validator(
        "status",
        pre=True,
        allow_reuse=True,
    )(normalize_status)


class TreatmentUpdate(BaseModel):

    patient_id: int | None = None

    treatment_name: str | None = None

    cost: int | None = Field(None, ge=0, le=100000000)

    status: TreatmentStatus | None = None

    notes: str | None = None

    treatment_date: datetime | None = None

    _normalize_status = validator(
        "status",
        pre=True,
        allow_reuse=True,
    )(normalize_status)


class TreatmentResponse(BaseModel):

    id: int

    patient_id: int

    treatment_name: str

    cost: int

    status: str

    notes: str | None = None

    treatment_date: datetime | None = None

    class Config:
        orm_mode = True
