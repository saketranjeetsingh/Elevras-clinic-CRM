from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.treatment import Treatment
from app.models.patient import Patient
from app.models.user import User

from app.schemas.treatment import TreatmentCreate
from app.schemas.treatment import TreatmentResponse
from app.schemas.treatment import TreatmentUpdate

from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission


router = APIRouter(
    prefix="/treatments",
    tags=["Treatments"]
)


@router.post("", response_model=TreatmentResponse)
@router.post("/", response_model=TreatmentResponse)
def create_treatment(
    treatment: TreatmentCreate,
    current_user: User = Depends(require_permission("treatment:create")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == treatment.patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    new_treatment = Treatment(
        organization_id=org_id,
        patient_id=treatment.patient_id,
        doctor_id=treatment.doctor_id,
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
    current_user: User = Depends(require_permission("treatment:view")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    return db.query(Treatment).filter(
        Treatment.organization_id == org_id
    ).all()


@router.put("/{treatment_id}", response_model=TreatmentResponse)
def update_treatment(
    treatment_id: int,
    treatment_data: TreatmentUpdate,
    current_user: User = Depends(require_permission("treatment:edit")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    treatment = db.query(Treatment).filter(
        Treatment.id == treatment_id,
        Treatment.organization_id == org_id
    ).first()

    if not treatment:
        raise HTTPException(
            status_code=404,
            detail="Treatment not found"
        )

    if treatment_data.patient_id is not None:
        patient = db.query(Patient).filter(
            Patient.id == treatment_data.patient_id,
            Patient.organization_id == org_id
        ).first()
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        treatment.patient_id = treatment_data.patient_id

    if treatment_data.doctor_id is not None:
        treatment.doctor_id = treatment_data.doctor_id

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
    current_user: User = Depends(require_permission("treatment:delete")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    treatment = db.query(Treatment).filter(
        Treatment.id == treatment_id,
        Treatment.organization_id == org_id,
    ).first()

    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    db.delete(treatment)
    db.commit()

    return {"message": "Treatment deleted successfully"}