from functools import wraps
from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.dependencies import get_current_user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user with full User object."""
    from app.security import verify_token
    from fastapi.security import OAuth2PasswordBearer

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    token = oauth2_scheme.__call__(request)

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")

    return user


def get_user_permissions(user: User, organization_id: int, db: Session) -> List[str]:
    """Get all permission codes for a user in an organization."""
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.organization_id == organization_id,
    ).all()

    if not user_roles:
        return []

    role_ids = [ur.role_id for ur in user_roles]

    permissions = db.query(Permission.code).join(
        RolePermission, Permission.id == RolePermission.permission_id
    ).filter(RolePermission.role_id.in_(role_ids)).all()

    return [p[0] for p in permissions]


def get_user_roles(user: User, organization_id: int, db: Session) -> List[str]:
    """Get all role codes for a user in an organization."""
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.organization_id == organization_id,
    ).all()

    if not user_roles:
        return []

    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role.code).filter(Role.id.in_(role_ids)).all()
    return [r[0] for r in roles]


def require_permission(permission_code: str):
    """Dependency factory that requires a specific permission."""
    def permission_checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        organization_id = request.headers.get("X-Organization-ID")
        if not organization_id:
            raise HTTPException(status_code=400, detail="Organization context required")

        try:
            org_id = int(organization_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid organization ID")

        permissions = get_user_permissions(current_user, org_id, db)
        if permission_code not in permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission_code} required",
            )

        # Attach org_id to request state for easy access in routers
        request.state.organization_id = org_id
        request.state.current_user = current_user
        request.state.user_permissions = permissions

        return current_user

    return permission_checker


def require_any_permission(permission_codes: List[str]):
    """Dependency factory that requires at least one of the given permissions."""
    def permission_checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        organization_id = request.headers.get("X-Organization-ID")
        if not organization_id:
            raise HTTPException(status_code=400, detail="Organization context required")

        try:
            org_id = int(organization_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid organization ID")

        permissions = get_user_permissions(current_user, org_id, db)
        if not any(p in permissions for p in permission_codes):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: one of {permission_codes} required",
            )

        request.state.organization_id = org_id
        request.state.current_user = current_user
        request.state.user_permissions = permissions

        return current_user

    return permission_checker


def get_organization_id(request: Request) -> int:
    """Extract organization_id from request state (set by permission checker)."""
    org_id = getattr(request.state, "organization_id", None)
    if org_id is None:
        org_id = request.headers.get("X-Organization-ID")
        if org_id:
            try:
                org_id = int(org_id)
            except ValueError:
                org_id = None

    if org_id is None:
        raise HTTPException(status_code=400, detail="Organization context required")

    return org_id


class PermissionChecker:
    """Class-based permission checker for use in router functions."""

    def __init__(self, permission_code: str):
        self.permission_code = permission_code

    def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        organization_id = request.headers.get("X-Organization-ID")
        if not organization_id:
            raise HTTPException(status_code=400, detail="Organization context required")

        try:
            org_id = int(organization_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid organization ID")

        permissions = get_user_permissions(current_user, org_id, db)
        if self.permission_code not in permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {self.permission_code} required",
            )

        request.state.organization_id = org_id
        request.state.current_user = current_user
        request.state.user_permissions = permissions

        return current_user