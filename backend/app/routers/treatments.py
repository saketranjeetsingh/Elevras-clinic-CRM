from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.treatment import Treatment

from app.schemas.treatment import TreatmentCreate


router = APIRouter(
    prefix="/treatments",
    tags=["Treatments"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/")
def create_treatment(
    treatment: TreatmentCreate,
    db: Session = Depends(get_db)
):

    new_treatment = Treatment(
        patient_id=treatment.patient_id,
        treatment_name=treatment.treatment_name,
        cost=treatment.cost,
        status=treatment.status,
        notes=treatment.notes
    )

    db.add(new_treatment)

    db.commit()

    db.refresh(new_treatment)

    return new_treatment


@router.get("/")
def get_treatments(
    db: Session = Depends(get_db)
):

    return db.query(Treatment).all()

    