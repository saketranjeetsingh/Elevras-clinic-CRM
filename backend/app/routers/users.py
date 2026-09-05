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
from app.models.doctor_profile import DoctorProfile

from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRoles
from app.schemas.doctor_profile import DoctorProfileCreate, DoctorProfileResponse
from app.dependencies import get_db
from app.dependencies import get_current_user_with_org
from app.dependencies import get_organization_id
from app.dependencies import require_permission
from app.security import hash_password
from app.audit import log_audit, get_client_ip


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("", response_model=UserResponse)
@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Create a new user in the current organization."""
    org_id = get_organization_id(request)

    # Check if user already exists globally
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        name=user_data.name,
        is_active=True,
    )
    db.add(user)
    db.flush()

    # Assign role in the organization
    role = db.query(Role).filter(Role.code == user_data.role_code, Role.organization_id.in_([org_id, None])).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{user_data.role_code}' not found")

    user_role = UserRole(
        user_id=user.id,
        role_id=role.id,
        organization_id=org_id,
    )
    db.add(user_role)
    db.commit()
    db.refresh(user)

    log_audit(db, org_id, current_user.id, "create", "user", user.id, None, {"email": user.email, "name": user.name, "role": role.code}, request.client.host if request and request.client else None)

    return user


@router.get("", response_model=list[UserWithRoles])
@router.get("/", response_model=list[UserWithRoles])
def list_users(
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """List all users in the current organization."""
    org_id = get_organization_id(request)

    user_roles = db.query(UserRole).filter(UserRole.organization_id == org_id).all()
    user_ids = [ur.user_id for ur in user_roles]

    if not user_ids:
        return []

    users = db.query(User).filter(User.id.in_(user_ids)).all()

    # Build response with roles
    result = []
    for user in users:
        ur_list = [ur for ur in user_roles if ur.user_id == user.id]
        roles = []
        permissions = []
        for ur in ur_list:
            role = db.query(Role).filter(Role.id == ur.role_id).first()
            if role:
                roles.append(role.code)
                # Get permissions
                from app.models.role_permission import RolePermission
                from app.models.permission import Permission
                perms = db.query(Permission.code).join(RolePermission, Permission.id == RolePermission.permission_id).filter(RolePermission.role_id == role.id).all()
                permissions.extend([p[0] for p in perms])

        result.append(UserWithRoles(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=roles,
            permissions=list(set(permissions)),
            organization_id=org_id,
        ))

    return result


@router.get("/{user_id}", response_model=UserWithRoles)
def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Get a specific user in the organization."""
    org_id = get_organization_id(request)

    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=404, detail="User not found in this organization")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == user_role.role_id).first()

    from app.models.role_permission import RolePermission
    from app.models.permission import Permission
    perms = db.query(Permission.code).join(RolePermission, Permission.id == RolePermission.permission_id).filter(RolePermission.role_id == role.id).all()
    permissions = [p[0] for p in perms]

    return UserWithRoles(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.code] if role else [],
        permissions=permissions,
        organization_id=org_id,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Update a user."""
    org_id = get_organization_id(request)

    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=404, detail="User not found in this organization")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    before = {"email": user.email, "name": user.name, "is_active": user.is_active}

    if user_data.email is not None:
        existing = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = user_data.email

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)

    log_audit(db, org_id, current_user.id, "update", "user", user.id, before, {"email": user.email, "name": user.name, "is_active": user.is_active}, request.client.host if request and request.client else None)

    return user


@router.post("/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Deactivate a user (soft delete)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    org_id = get_organization_id(request)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=403, detail="User not in this organization")

    user.is_active = False
    db.commit()

    log_audit(db, org_id, current_user.id, "deactivate", "user", user_id, {"is_active": True}, {"is_active": False}, request.client.host if request and request.client else None)

    return {"message": "User deactivated successfully"}


@router.post("/{user_id}/activate")
def activate_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Activate a deactivated user."""
    org_id = get_organization_id(request)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=403, detail="User not in this organization")

    user.is_active = True
    db.commit()

    log_audit(db, org_id, current_user.id, "activate", "user", user_id, {"is_active": False}, {"is_active": True}, request.client.host if request and request.client else None)

    return {"message": "User activated successfully"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Delete a user permanently (hard delete)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    org_id = get_organization_id(request)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.organization_id == org_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=403, detail="User not in this organization")

    # Check for associated data
    from app.models.patient import Patient
    from app.models.appointment import Appointment
    from app.models.treatment import Treatment
    from app.models.bill import Bill

    has_data = any([
        db.query(Patient).filter(Patient.doctor_id == user_id).first(),
        db.query(Appointment).filter(Appointment.doctor_id == user_id).first(),
        db.query(Treatment).filter(Treatment.doctor_id == user_id).first(),
        db.query(Bill).filter(Bill.doctor_id == user_id).first(),
    ])

    if has_data:
        raise HTTPException(
            status_code=409,
            detail="User has associated data. Reassign data first or deactivate instead."
        )

    log_audit(db, org_id, current_user.id, "delete", "user", user_id, {"email": user.email}, None, request.client.host if request and request.client else None)

    db.delete(user_role)
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}