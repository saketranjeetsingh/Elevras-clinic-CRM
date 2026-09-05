import os
import uuid
from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.attachment import PatientAttachment
from app.models.patient import Patient
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission


router = APIRouter(
    tags=["Attachments"]
)

CATEGORIES = {"x-ray", "prescription", "lab-report", "photo", "other"}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


def _upload_dir() -> str:
    return os.environ.get("UPLOAD_DIR", DEFAULT_UPLOAD_DIR)


def _max_upload_bytes() -> int:
    try:
        mega_bytes = int(os.environ.get("MAX_UPLOAD_MB", "20"))
    except (TypeError, ValueError):
        mega_bytes = 20
    return mega_bytes * 1024 * 1024


def _attachment_to_dict(attachment: PatientAttachment) -> dict:
    return {
        "id": attachment.id,
        "patient_id": attachment.patient_id,
        "filename": attachment.filename,
        "content_type": attachment.content_type,
        "size": attachment.size,
        "category": attachment.category,
        "notes": attachment.notes,
        "created_at": attachment.created_at,
    }


def _attachment_path(attachment: PatientAttachment) -> Path:
    return Path(_upload_dir()) / str(attachment.organization_id) / str(attachment.patient_id) / attachment.stored_name


def _safe_suffix(filename: str) -> str:
    suffix = Path(filename or "").suffix.lower()
    if len(suffix) > 10 or not suffix.startswith("."):
        return ""
    return suffix


@router.post("/patients/{patient_id}/attachments", response_model=AttachmentResponse)
def upload_patient_attachment(
    patient_id: int,
    file: UploadFile = File(...),
    category: str = Form("other"),
    notes: str = Form(""),
    current_user: User = Depends(require_permission("attachment:upload")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Upload images or PDF files.",
        )

    category_value = (category or "other").strip().lower()
    if category_value not in CATEGORIES:
        category_value = "other"

    content = file.file.read()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    max_bytes = _max_upload_bytes()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Maximum size is {max_bytes // (1024 * 1024)} MB.",
        )

    stored_name = f"{uuid.uuid4().hex}{_safe_suffix(file.filename or '')}"
    upload_path = Path(_upload_dir()) / str(org_id) / str(patient_id)
    upload_path.mkdir(parents=True, exist_ok=True)

    file_path = upload_path / stored_name
    with open(file_path, "wb") as target:
        target.write(content)

    attachment = PatientAttachment(
        organization_id=org_id,
        patient_id=patient_id,
        doctor_id=current_user.id,
        filename=(file.filename or "file").strip(),
        stored_name=stored_name,
        content_type=content_type,
        size=len(content),
        category=category_value,
        notes=notes.strip() or None,
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


@router.get("/patients/{patient_id}/attachments", response_model=list[AttachmentResponse])
def list_patient_attachments(
    patient_id: int,
    current_user: User = Depends(require_permission("attachment:view")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.organization_id == org_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return db.query(PatientAttachment).filter(
        PatientAttachment.patient_id == patient_id,
        PatientAttachment.organization_id == org_id,
    ).order_by(PatientAttachment.created_at.desc(), PatientAttachment.id.desc()).all()


@router.get("/attachments/{attachment_id}/file")
def download_attachment(
    attachment_id: int,
    current_user: User = Depends(require_permission("attachment:view")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    attachment = db.query(PatientAttachment).filter(
        PatientAttachment.id == attachment_id,
        PatientAttachment.organization_id == org_id,
    ).first()

    if not attachment:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found"
        )

    file_path = _attachment_path(attachment)
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Attachment file is missing"
        )

    return FileResponse(
        path=str(file_path),
        media_type=attachment.content_type,
        filename=attachment.filename,
    )


@router.delete("/patients/{patient_id}/attachments/{attachment_id}")
def delete_patient_attachment(
    patient_id: int,
    attachment_id: int,
    current_user: User = Depends(require_permission("attachment:delete")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.organization_id == org_id,
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    attachment = db.query(PatientAttachment).filter(
        PatientAttachment.id == attachment_id,
        PatientAttachment.patient_id == patient_id,
        PatientAttachment.organization_id == org_id,
    ).first()

    if not attachment:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found"
        )

    file_path = _attachment_path(attachment)
    db.delete(attachment)
    db.commit()

    try:
        if file_path.is_file():
            file_path.unlink()
    except OSError:
        pass

    return {
        "message": "Attachment deleted successfully"
    }