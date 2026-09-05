from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DoctorProfileBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    registration_number: Optional[str] = None
    color: str = "#3B82F6"
    is_active: bool = True


class DoctorProfileCreate(DoctorProfileBase):
    pass


class DoctorProfileUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    registration_number: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class DoctorProfileResponse(DoctorProfileBase):
    id: int
    user_id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
