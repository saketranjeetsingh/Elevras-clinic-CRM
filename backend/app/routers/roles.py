from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole

from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions, PermissionResponse
from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission
from app.audit import log_audit, get_client_ip


router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    current_user: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
):
    """List all available permissions."""
    perms = db.query(Permission).order_by(Permission.code).all()
    return perms


@router.post("", response_model=RoleResponse)
@router.post("/", response_model=RoleResponse)
def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Create a custom role for the organization."""
    org_id = get_organization_id(request)

    existing = db.query(Role).filter(Role.code == role_data.code, Role.organization_id == org_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Role code already exists in this organization")

    role = Role(
        name=role_data.name,
        code=role_data.code,
        organization_id=org_id,
    )
    db.add(role)
    db.flush()

    if role_data.permission_codes:
        perms = db.query(Permission).filter(Permission.code.in_(role_data.permission_codes)).all()
        for perm in perms:
            rp = RolePermission(role_id=role.id, permission_id=perm.id)
            db.add(rp)

    db.commit()
    db.refresh(role)

    log_audit(db, org_id, current_user.id, "create", "role", role.id, None, {"name": role.name, "code": role.code}, request.client.host if request and request.client else None)

    return role


@router.get("", response_model=list[RoleWithPermissions])
@router.get("/", response_model=list[RoleWithPermissions])
def list_roles(
    current_user: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """List all roles (system + organization-specific)."""
    org_id = get_organization_id(request)

    roles = db.query(Role).filter(
        (Role.organization_id == org_id) | (Role.organization_id.is_(None))
    ).order_by(Role.organization_id, Role.code).all()

    result = []
    for role in roles:
        perms = db.query(Permission.code).join(RolePermission, Permission.id == RolePermission.permission_id).filter(RolePermission.role_id == role.id).all()
        permission_codes = [p[0] for p in perms]

        result.append(RoleWithPermissions(
            id=role.id,
            name=role.name,
            code=role.code,
            organization_id=role.organization_id,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=permission_codes,
        ))

    return result


@router.get("/{role_id}", response_model=RoleWithPermissions)
def get_role(
    role_id: int,
    current_user: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Get a specific role."""
    org_id = get_organization_id(request)

    role = db.query(Role).filter(
        Role.id == role_id,
        (Role.organization_id == org_id) | (Role.organization_id.is_(None))
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    perms = db.query(Permission.code).join(RolePermission, Permission.id == RolePermission.permission_id).filter(RolePermission.role_id == role.id).all()
    permission_codes = [p[0] for p in perms]

    return RoleWithPermissions(
        id=role.id,
        name=role.name,
        code=role.code,
        organization_id=role.organization_id,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=permission_codes,
    )


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Update a role (organization-specific only)."""
    org_id = get_organization_id(request)

    role = db.query(Role).filter(
        Role.id == role_id,
        Role.organization_id == org_id,
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found or cannot modify system role")

    before = {"name": role.name}

    if role_data.name is not None:
        role.name = role_data.name

    if role_data.permission_codes is not None:
        # Update permissions
        db.query(RolePermission).filter(RolePermission.role_id == role.id).delete()
        perms = db.query(Permission).filter(Permission.code.in_(role_data.permission_codes)).all()
        for perm in perms:
            rp = RolePermission(role_id=role.id, permission_id=perm.id)
            db.add(rp)

    db.commit()
    db.refresh(role)

    log_audit(db, org_id, current_user.id, "update", "role", role.id, before, {"name": role.name}, request.client.host if request and request.client else None)

    return role


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    current_user: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Delete a custom role (organization-specific only)."""
    org_id = get_organization_id(request)

    role = db.query(Role).filter(
        Role.id == role_id,
        Role.organization_id == org_id,
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found or cannot delete system role")

    # Check if role is assigned to any users
    user_count = db.query(UserRole).filter(UserRole.role_id == role_id).count()
    if user_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Role is assigned to {user_count} user(s). Reassign them first."
        )

    log_audit(db, org_id, current_user.id, "delete", "role", role.id, {"name": role.name, "code": role.code}, None, request.client.host if request and request.client else None)

    db.delete(role)
    db.commit()

    return {"message": "Role deleted successfully"}


@router.post("/{role_id}/assign")
def assign_role_to_user(
    role_id: int,
    user_id: int,
    current_user: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Assign a role to a user in the organization."""
    org_id = get_organization_id(request)

    role = db.query(Role).filter(
        Role.id == role_id,
        (Role.organization_id == org_id) | (Role.organization_id.is_(None))
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is in this organization
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=403, detail="User not in this organization")

    # Update user's role
    user_role.role_id = role_id
    db.commit()

    log_audit(db, org_id, current_user.id, "assign_role", "user", user_id, {"old_role_id": user_role.role_id}, {"new_role_id": role_id}, request.client.host if request and request.client else None)

    return {"message": "Role assigned successfully"}