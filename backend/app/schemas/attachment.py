from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AttachmentBase(BaseModel):
    patient_id: int
    filename: str
    content_type: str
    size: int
    category: str
    notes: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    pass


class AttachmentResponse(AttachmentBase):
    id: int
    organization_id: int
    doctor_id: int
    created_at: datetime

    class Config:
        orm_mode = True
