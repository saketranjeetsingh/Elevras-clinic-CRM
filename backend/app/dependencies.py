from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.patient import Patient
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.security import verify_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from access token."""
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User is inactive"
        )

    return user


def get_current_user_with_org(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Get current user with organization context from header."""
    organization_id = request.headers.get("X-Organization-ID")
    if not organization_id:
        raise HTTPException(
            status_code=400,
            detail="Organization context required (X-Organization-ID header)"
        )

    try:
        org_id = int(organization_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid organization ID"
        )

    # Verify user has access to this organization
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(
            status_code=403,
            detail="No access to this organization"
        )

    # Attach to request state for use in routers
    request.state.organization_id = org_id
    request.state.current_user = current_user

    return current_user


def require_permission(permission_code: str):
    """Dependency factory that requires a specific permission in the current organization."""
    def permission_checker(
        request: Request,
        current_user: User = Depends(get_current_user_with_org),
        db: Session = Depends(get_db),
    ) -> User:
        org_id = request.state.organization_id

        # Get user's permissions in this organization
        user_roles = db.query(UserRole).filter(
            UserRole.user_id == current_user.id,
            UserRole.organization_id == org_id,
        ).all()

        if not user_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission_code} required"
            )

        role_ids = [ur.role_id for ur in user_roles]
        permissions = db.query(Permission.code).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(RolePermission.role_id.in_(role_ids)).all()

        permission_codes = [p[0] for p in permissions]
        if permission_code not in permission_codes:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission_code} required"
            )

        request.state.user_permissions = permission_codes
        return current_user

    return permission_checker


def get_organization_id(request: Request) -> int:
    """Extract organization_id from request state (set by permission checker)."""
    org_id = getattr(request.state, "organization_id", None)
    if org_id is None:
        raise HTTPException(status_code=400, detail="Organization context required")
    return org_id


def get_patient_for_current_user(
    patient_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_with_org),
    db: Session = Depends(get_db),
) -> Patient:
    """Get patient ensuring it belongs to the current organization."""
    org_id = get_organization_id(request)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.organization_id == org_id,
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient