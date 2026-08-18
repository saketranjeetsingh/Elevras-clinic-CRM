from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.treatment import Treatment

from app.schemas.treatment import TreatmentCreate
from app.schemas.treatment import TreatmentResponse
from app.schemas.treatment import TreatmentUpdate

from app.dependencies import get_current_doctor
from app.dependencies import get_patient_for_current_doctor


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


@router.post("", response_model=TreatmentResponse)
@router.post("/", response_model=TreatmentResponse)
def create_treatment(
    treatment: TreatmentCreate,
    current_doctor: dict = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db)
):

    get_patient_for_current_doctor(
        treatment.patient_id,
        current_doctor,
        db
    )

    new_treatment = Treatment(
        doctor_id=current_doctor["doctor_id"],
        patient_id=treatment.patient_id,
        treatment_name=treatment.treatment_name,
        cost=treatment.cost,
        status=treatment.status,
        notes=treatment.notes,
        treatment_date=treatment.treatment_date,
    )

    db.add(new_treatment)

    db.commit()

    db.refresh(new_treatment)

    return new_treatment


@router.get("", response_model=list[TreatmentResponse])
@router.get("/", response_model=list[TreatmentResponse])
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


@router.put("/{treatment_id}", response_model=TreatmentResponse)
def update_treatment(
    treatment_id: int,
    treatment_data: TreatmentUpdate,
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
        raise HTTPException(
            status_code=404,
            detail="Treatment not found"
        )

    if treatment_data.patient_id is not None:
        get_patient_for_current_doctor(treatment_data.patient_id, current_doctor, db)
        treatment.patient_id = treatment_data.patient_id

    if treatment_data.treatment_name is not None:
        treatment.treatment_name = treatment_data.treatment_name

    if treatment_data.cost is not None:
        treatment.cost = treatment_data.cost

    if treatment_data.status is not None:
        treatment.status = treatment_data.status

    if treatment_data.notes is not None:
        treatment.notes = treatment_data.notes

    if treatment_data.treatment_date is not None:
        treatment.treatment_date = treatment_data.treatment_date

    db.commit()

    db.refresh(treatment)

    return treatment


@router.delete("/{treatment_id}")
def delete_treatment(
    treatment_id: int,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    treatment = db.query(Treatment).filter(
        Treatment.id == treatment_id,
        Treatment.doctor_id == current_doctor["doctor_id"],
    ).first()

    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    db.delete(treatment)
    db.commit()

    return {"message": "Treatment deleted successfully"}