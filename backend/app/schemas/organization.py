from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class OrganizationBase(BaseModel):
    name: str
    slug: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class OrganizationWithStats(OrganizationResponse):
    user_count: int = 0
    patient_count: int = 0
