from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.treatment import Treatment

from app.schemas.treatment import TreatmentCreate

from app.dependencies import get_current_doctor


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
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    new_treatment = Treatment(
        doctor_id=current_doctor["doctor_id"],
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
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    return db.query(Treatment).filter(
        Treatment.doctor_id ==
        current_doctor["doctor_id"]
    ).all()


@router.put("/{treatment_id}")
def update_treatment_status(
    treatment_id: int,
    status: str,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    treatment = db.query(Treatment).filter(
        Treatment.id == treatment_id,
        Treatment.doctor_id == current_doctor["doctor_id"]
    ).first()

    if not treatment:
        return {
            "message": "Treatment not found"
        }

    treatment.status = status

    db.commit()

    db.refresh(treatment)

    return treatment