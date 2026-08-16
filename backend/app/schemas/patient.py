from pydantic import BaseModel


class PatientCreate(BaseModel):
    name: str
    phone: str
    email: str
    age: int | None = None
    gender: str | None = None
    address: str | None = None
    blood_group: str | None = None
    medical_history: str | None = None
    notes: str | None = None


class PatientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    age: int | None = None
    gender: str | None = None
    address: str | None = None
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
    address: str | None = None
    blood_group: str | None = None
    medical_history: str | None = None
    notes: str | None = None
    last_treatment: str | None = None

    class Config:
        from_attributes = True