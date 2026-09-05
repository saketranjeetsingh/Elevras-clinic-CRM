from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import User
from app.schemas.appointment import AppointmentCreate
from app.schemas.appointment import AppointmentResponse
from app.schemas.appointment import AppointmentUpdate
from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("", response_model=AppointmentResponse)
@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(require_permission("appointment:create")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == appointment.patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    new_appointment = Appointment(
        organization_id=org_id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        doctor_name=appointment.doctor_name,
        start_at=appointment.start_at,
        end_at=appointment.end_at,
        status=appointment.status,
        notes=appointment.notes
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@router.get("", response_model=list[AppointmentResponse])
@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(
    current_user: User = Depends(require_permission("appointment:view")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    return db.query(Appointment).filter(
        Appointment.organization_id == org_id
    ).all()


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(require_permission("appointment:edit")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.organization_id == org_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    if appointment_data.patient_id is not None:
        patient = db.query(Patient).filter(
            Patient.id == appointment_data.patient_id,
            Patient.organization_id == org_id
        ).first()
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        appointment.patient_id = appointment_data.patient_id

    if appointment_data.doctor_id is not None:
        appointment.doctor_id = appointment_data.doctor_id

    if appointment_data.doctor_name is not None:
        appointment.doctor_name = appointment_data.doctor_name

    if appointment_data.start_at is not None:
        appointment.start_at = appointment_data.start_at

    if appointment_data.end_at is not None:
        appointment.end_at = appointment_data.end_at

    if appointment_data.status is not None:
        appointment.status = appointment_data.status

    if appointment_data.notes is not None:
        appointment.notes = appointment_data.notes

    db.commit()
    db.refresh(appointment)

    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    current_user: User = Depends(require_permission("appointment:delete")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.organization_id == org_id,
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment deleted successfully"}