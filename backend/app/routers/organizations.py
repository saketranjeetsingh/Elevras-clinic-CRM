from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.organization import Organization
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role

from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse, OrganizationWithStats
from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission
from app.audit import log_audit, get_client_ip


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


@router.post("", response_model=OrganizationResponse)
@router.post("/", response_model=OrganizationResponse)
def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(require_permission("org:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Create a new organization (admin only)."""
    existing = db.query(Organization).filter(Organization.slug == org_data.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Organization slug already exists")

    org = Organization(name=org_data.name, slug=org_data.slug)
    db.add(org)
    db.commit()
    db.refresh(org)

    log_audit(db, org.id, current_user.id, "create", "organization", org.id, None, {"name": org.name, "slug": org.slug}, request.client.host if request and request.client else None)

    return org


@router.get("", response_model=list[OrganizationResponse])
@router.get("/", response_model=list[OrganizationResponse])
def list_organizations(
    current_user: User = Depends(require_permission("org:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """List organizations the user has access to."""
    # For now, only return organizations where user has a role
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    org_ids = [ur.organization_id for ur in user_roles]

    if not org_ids:
        return []

    orgs = db.query(Organization).filter(Organization.id.in_(org_ids)).all()
    return orgs


@router.get("/me", response_model=OrganizationWithStats)
def get_my_organization(
    current_user: User = Depends(get_current_user_with_org),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Get current organization with stats."""
    org_id = get_organization_id(request)
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Get stats
    from app.models.patient import Patient
    user_count = db.query(UserRole).filter(UserRole.organization_id == org_id).count()
    patient_count = db.query(Patient).filter(Patient.organization_id == org_id).count()

    return OrganizationWithStats(
        id=org.id,
        name=org.name,
        slug=org.slug,
        created_at=org.created_at,
        updated_at=org.updated_at,
        user_count=user_count,
        patient_count=patient_count,
    )


@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(require_permission("org:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Update organization settings."""
    # Verify user has access to this org
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=403, detail="No access to this organization")

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    before = {"name": org.name, "slug": org.slug}

    if org_data.name is not None:
        org.name = org_data.name

    if org_data.slug is not None:
        existing = db.query(Organization).filter(Organization.slug == org_data.slug, Organization.id != org_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Organization slug already exists")
        org.slug = org_data.slug

    db.commit()
    db.refresh(org)

    log_audit(db, org.id, current_user.id, "update", "organization", org.id, before, {"name": org.name, "slug": org.slug}, request.client.host if request and request.client else None)

    return org


@router.delete("/{org_id}")
def delete_organization(
    org_id: int,
    current_user: User = Depends(require_permission("org:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Delete an organization (soft delete not implemented, hard delete)."""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=403, detail="No access to this organization")

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if there's data - for safety, require explicit confirmation
    from app.models.patient import Patient
    from app.models.appointment import Appointment
    from app.models.treatment import Treatment
    from app.models.bill import Bill

    has_data = any([
        db.query(Patient).filter(Patient.organization_id == org_id).first(),
        db.query(Appointment).filter(Appointment.organization_id == org_id).first(),
        db.query(Treatment).filter(Treatment.organization_id == org_id).first(),
        db.query(Bill).filter(Bill.organization_id == org_id).first(),
    ])

    if has_data:
        raise HTTPException(
            status_code=409,
            detail="Organization has data. Delete all data first or contact support."
        )

    log_audit(db, org.id, current_user.id, "delete", "organization", org.id, {"name": org.name}, None, request.client.host if request and request.client else None)

    db.delete(org)
    db.commit()

    return {"message": "Organization deleted successfully"}