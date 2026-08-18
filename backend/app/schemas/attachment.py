from datetime import datetime

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: int
    patient_id: int
    filename: str
    content_type: str
    size: int
    category: str
    notes: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True