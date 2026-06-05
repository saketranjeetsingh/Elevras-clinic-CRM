from pydantic import BaseModel


class PatientCreate(BaseModel):
    name: str
    phone: str
    email: str
    age: int
    gender: str
    notes: str
    last_treatment: str


class PatientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    age: int | None = None
    gender: str | None = None
    notes: str | None = None
    last_treatment: str | None = None


class PatientResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    age: int
    gender: str
    notes: str
    last_treatment: str

    class Config:
        from_attributes = True