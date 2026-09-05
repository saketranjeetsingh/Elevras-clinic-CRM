from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class DoctorSignup(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)
    clinic_name: str = Field(min_length=1)


class DoctorLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class DoctorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    clinic_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
