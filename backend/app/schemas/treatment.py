from pydantic import BaseModel


class TreatmentCreate(BaseModel):

    patient_id: int
    treatment_name: str
    cost: int
    status: str
    notes: str


class TreatmentResponse(BaseModel):

    id: int
    patient_id: int
    treatment_name: str
    cost: int
    status: str
    notes: str

    class Config:
        from_attributes = True