from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.user import User
from app.models.organization import Organization
from app.models.doctor_profile import DoctorProfile
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog

from app.schemas.user import UserCreate
from app.schemas.organization import OrganizationCreate

from app.security import hash_password
from app.security import verify_password
from app.security import create_access_token
from app.security import create_refresh_token
from app.security import hash_refresh_token
from app.security import verify_refresh_token

from app.ratelimit import auth_rate_limit
from app.constants import DEFAULT_ROLE_PERMISSIONS


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_permissions(user: User, organization_id: int, db: Session):
    """Get all permission codes for a user in an organization."""
    from app.models.user_role import UserRole
    from app.models.role_permission import RolePermission
    from app.models.permission import Permission

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


def get_user_roles(user: User, organization_id: int, db: Session):
    """Get all role codes for a user in an organization."""
    from app.models.user_role import UserRole
    from app.models.role import Role

    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.organization_id == organization_id,
    ).all()

    if not user_roles:
        return []

    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role.code).filter(Role.id.in_(role_ids)).all()
    return [r[0] for r in roles]


def log_audit(db: Session, organization_id: int | None, actor_user_id: int | None, action: str, entity_type: str, entity_id: int | None, before: dict | None, after: dict | None, ip_address: str | None):
    """Log an audit event."""
    try:
        audit = AuditLog(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=str(before) if before else None,
            after=str(after) if after else None,
            ip_address=ip_address,
        )
        db.add(audit)
        db.commit()
    except Exception:
        db.rollback()


@router.post("/signup")
def signup(
    user_data: UserCreate,
    _: None = Depends(auth_rate_limit),
    db: Session = Depends(get_db)
):
    """Create a new organization with an admin user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create organization
    org_name = f"{user_data.name}'s Clinic"
    slug_base = org_name.lower().replace(" ", "-").replace("'", "")
    slug = slug_base
    counter = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        counter += 1
        slug = f"{slug_base}-{counter}"

    org = Organization(name=org_name, slug=slug)
    db.add(org)
    db.flush()

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        name=user_data.name,
        is_active=True,
    )
    db.add(user)
    db.flush()

    # Create doctor profile
    doctor_profile = DoctorProfile(
        user_id=user.id,
        organization_id=org.id,
        name=user_data.name,
        is_active=True,
        color="#3B82F6",
    )
    db.add(doctor_profile)
    db.flush()

    # Assign Admin role
    admin_role = db.query(Role).filter(Role.code == "admin", Role.organization_id.is_(None)).first()
    if admin_role:
        user_role = UserRole(
            user_id=user.id,
            role_id=admin_role.id,
            organization_id=org.id,
        )
        db.add(user_role)

    db.commit()

    # Log audit
    log_audit(db, org.id, user.id, "signup", "user", user.id, None, {"email": user.email, "name": user.name}, None)

    return {
        "message": "Organization and admin user created successfully",
        "organization_id": org.id,
    }


@router.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    _: None = Depends(auth_rate_limit),
    db: Session = Depends(get_db),
    request: Request = None,
):
    email = form_data.username
    password = form_data.password

    if not email or not password:
        raise HTTPException(status_code=422, detail="Validation failed")

    db_user = db.query(User).filter(User.email == email).first()

    if not db_user:
        log_audit(db, None, None, "login_failed", "user", None, None, {"email": email}, request.client.host if request and request.client else None)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, db_user.hashed_password):
        log_audit(db, None, db_user.id, "login_failed", "user", db_user.id, None, {"email": email}, request.client.host if request and request.client else None)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")

    # Get user's organizations and roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == db_user.id).all()
    org_roles = {}
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            if ur.organization_id not in org_roles:
                org_roles[ur.organization_id] = []
            org_roles[ur.organization_id].append(role.code)

    # Default to first organization if multiple
    default_org_id = user_roles[0].organization_id if user_roles else None
    default_roles = org_roles.get(default_org_id, []) if default_org_id else []
    default_permissions = get_user_permissions(db_user, default_org_id, db) if default_org_id else []

    # Get doctor profile for the default organization
    doctor_profile = None
    if default_org_id:
        doctor_profile = db.query(DoctorProfile).filter(
            DoctorProfile.user_id == db_user.id,
            DoctorProfile.organization_id == default_org_id,
        ).first()

    # Create access token
    access_token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email,
        "organization_id": default_org_id,
        "roles": default_roles,
        "permissions": default_permissions,
    })

    # Create refresh token
    refresh_token = create_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    refresh_token_obj = RefreshToken(
        user_id=db_user.id,
        token_hash=refresh_token_hash,
        is_revoked=False,
        expires_at=expires_at,
    )
    db.add(refresh_token_obj)
    db.commit()

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
        path="/auth/refresh",
    )

    log_audit(db, default_org_id, db_user.id, "login", "user", db_user.id, None, {"email": email}, request.client.host if request and request.client else None)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "organization_id": default_org_id,
            "roles": default_roles,
            "permissions": default_permissions,
            "organizations": list(org_roles.keys()),
            "doctor_profile_id": doctor_profile.id if doctor_profile else None,
        },
    }


@router.post("/refresh")
def refresh_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token from cookie."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    # Find matching refresh token
    # We need to check all refresh tokens for the user (inefficient but secure)
    # Better: store a token identifier in the token itself
    all_tokens = db.query(RefreshToken).filter(RefreshToken.is_revoked == False).all()

    valid_token_obj = None
    for rt in all_tokens:
        if verify_refresh_token(refresh_token, rt.token_hash):
            if rt.expires_at > datetime.now(timezone.utc):
                valid_token_obj = rt
                break

    if not valid_token_obj:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    db_user = db.query(User).filter(User.id == valid_token_obj.user_id).first()
    if not db_user or not db_user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Get user's organizations and roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == db_user.id).all()
    org_roles = {}
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            if ur.organization_id not in org_roles:
                org_roles[ur.organization_id] = []
            org_roles[ur.organization_id].append(role.code)

    # Use organization from request header or default
    org_id_header = request.headers.get("X-Organization-ID")
    default_org_id = None
    if org_id_header:
        try:
            default_org_id = int(org_id_header)
        except ValueError:
            pass

    if default_org_id is None and user_roles:
        default_org_id = user_roles[0].organization_id

    default_roles = org_roles.get(default_org_id, []) if default_org_id else []
    default_permissions = get_user_permissions(db_user, default_org_id, db) if default_org_id else []

    # Get doctor profile for the default organization
    doctor_profile = None
    if default_org_id:
        doctor_profile = db.query(DoctorProfile).filter(
            DoctorProfile.user_id == db_user.id,
            DoctorProfile.organization_id == default_org_id,
        ).first()

    # Create new access token
    access_token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email,
        "organization_id": default_org_id,
        "roles": default_roles,
        "permissions": default_permissions,
    })

    # Rotate refresh token (invalidate old, create new)
    valid_token_obj.is_revoked = True
    new_refresh_token = create_refresh_token()
    new_refresh_token_hash = hash_refresh_token(new_refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    new_refresh_token_obj = RefreshToken(
        user_id=db_user.id,
        token_hash=new_refresh_token_hash,
        is_revoked=False,
        expires_at=expires_at,
    )
    db.add(new_refresh_token_obj)
    db.commit()

    # Set new refresh token in cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
        path="/auth/refresh",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "organization_id": default_org_id,
            "roles": default_roles,
            "permissions": default_permissions,
            "organizations": list(org_roles.keys()),
            "doctor_profile_id": doctor_profile.id if doctor_profile else None,
        },
    }


@router.post("/logout")
def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    """Logout by revoking refresh token."""
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        all_tokens = db.query(RefreshToken).filter(RefreshToken.is_revoked == False).all()
        for rt in all_tokens:
            if verify_refresh_token(refresh_token, rt.token_hash):
                rt.is_revoked = True
                break
        db.commit()

    # Clear cookie
    response.delete_cookie(key="refresh_token", path="/auth/refresh")

    return {"message": "Logged out successfully"}


@router.post("/switch-organization")
def switch_organization(
    organization_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Switch active organization and return new access token."""
    # Verify user has access to this organization
    # In a real implementation, we'd get the current user from the access token
    # For now, we'll use the refresh token to identify the user
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    all_tokens = db.query(RefreshToken).filter(RefreshToken.is_revoked == False).all()
    valid_token_obj = None
    for rt in all_tokens:
        if verify_refresh_token(refresh_token, rt.token_hash):
            if rt.expires_at > datetime.now(timezone.utc):
                valid_token_obj = rt
                break

    if not valid_token_obj:
        raise HTTPException(status_code=401, detail="Invalid session")

    # Check if user has a role in this organization
    user_role = db.query(UserRole).filter(
        UserRole.user_id == valid_token_obj.user_id,
        UserRole.organization_id == organization_id,
    ).first()

    if not user_role:
        raise HTTPException(status_code=403, detail="No access to this organization")

    db_user = db.query(User).filter(User.id == valid_token_obj.user_id).first()
    if not db_user or not db_user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Get roles and permissions for the new organization
    roles = get_user_roles(db_user, organization_id, db)
    permissions = get_user_permissions(db_user, organization_id, db)

    access_token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email,
        "organization_id": organization_id,
        "roles": roles,
        "permissions": permissions,
    })

    # Get doctor profile for the new organization
    doctor_profile = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == db_user.id,
        DoctorProfile.organization_id == organization_id,
    ).first()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "organization_id": organization_id,
            "roles": roles,
            "permissions": permissions,
            "doctor_profile_id": doctor_profile.id if doctor_profile else None,
        },
    }


@router.get("/me")
async def get_me(
    request: Request,
    db: Session = Depends(get_db),
):
    """Get current user info from access token."""
    from app.security import verify_token
    from fastapi.security import OAuth2PasswordBearer

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    token = await oauth2_scheme.__call__(request)

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    org_id = payload.get("organization_id")
    roles = payload.get("roles", [])
    permissions = payload.get("permissions", [])

    # Get doctor profile for the organization
    doctor_profile = None
    if org_id:
        doctor_profile = db.query(DoctorProfile).filter(
            DoctorProfile.user_id == db_user.id,
            DoctorProfile.organization_id == org_id,
        ).first()

    return {
        "id": db_user.id,
        "email": db_user.email,
        "name": db_user.name,
        "is_active": db_user.is_active,
        "organization_id": org_id,
        "roles": roles,
        "permissions": permissions,
        "doctor_profile_id": doctor_profile.id if doctor_profile else None,
    }