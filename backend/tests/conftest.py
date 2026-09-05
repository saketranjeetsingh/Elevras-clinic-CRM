import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:lmaoyaarcomeon@localhost:5432/elevras_db_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-for-tests")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.routers import auth as auth_router
from app.routers import patients as patients_router
from app.routers import appointments as appointments_router
from app.routers import treatments as treatments_router
from app.routers import bills as bills_router
from app.routers import dashboard as dashboard_router
from app.routers import attachments as attachments_router
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_roles_and_permissions(db):
    """Seed the roles and permissions required for tests."""
    # Seed permissions
    all_permissions = [
        ("patient:view", "View patient records"),
        ("patient:create", "Create patient records"),
        ("patient:edit", "Edit patient records"),
        ("patient:delete", "Delete patient records"),
        ("patient:merge", "Merge duplicate patients"),
        ("appointment:view", "View appointments"),
        ("appointment:create", "Create appointments"),
        ("appointment:edit", "Edit appointments"),
        ("appointment:delete", "Delete appointments"),
        ("appointment:checkin", "Check-in patients"),
        ("treatment:view", "View treatments"),
        ("treatment:create", "Create treatments"),
        ("treatment:edit", "Edit treatments"),
        ("treatment:delete", "Delete treatments"),
        ("bill:view", "View bills"),
        ("bill:create", "Create bills"),
        ("bill:edit", "Edit bills"),
        ("bill:delete", "Delete bills"),
        ("bill:refund", "Process refunds"),
        ("dashboard:view", "View dashboard"),
        ("attachment:view", "View attachments"),
        ("attachment:upload", "Upload attachments"),
        ("attachment:delete", "Delete attachments"),
        ("role:manage", "Manage roles and permissions"),
        ("user:manage", "Manage users"),
        ("org:manage", "Manage organization settings"),
    ]
    
    for code, desc in all_permissions:
        if not db.query(Permission).filter(Permission.code == code).first():
            perm = Permission(code=code, description=desc)
            db.add(perm)
    
    db.flush()
    
    # Seed system roles
    admin_role = Role(name="Admin", code="admin", organization_id=None)
    doctor_role = Role(name="Doctor", code="doctor", organization_id=None)
    receptionist_role = Role(name="Receptionist", code="receptionist", organization_id=None)
    
    db.add_all([admin_role, doctor_role, receptionist_role])
    db.flush()
    
    # Assign permissions to roles
    all_perm_codes = [p[0] for p in all_permissions]
    doctor_perms = [
        "patient:view", "patient:create", "patient:edit",
        "appointment:view", "appointment:create", "appointment:edit", "appointment:checkin",
        "treatment:view", "treatment:create", "treatment:edit",
        "bill:view", "bill:create", "bill:edit",
        "dashboard:view",
        "attachment:view", "attachment:upload", "attachment:delete",
    ]
    receptionist_perms = [
        "patient:view", "patient:create", "patient:edit",
        "appointment:view", "appointment:create", "appointment:edit", "appointment:checkin",
        "bill:view", "bill:create", "bill:edit",
        "dashboard:view",
        "attachment:view", "attachment:upload",
    ]
    
    # Admin gets all permissions
    for code in all_perm_codes:
        perm = db.query(Permission).filter(Permission.code == code).first()
        if perm:
            rp = RolePermission(role_id=admin_role.id, permission_id=perm.id)
            db.add(rp)
    
    # Doctor permissions
    for code in doctor_perms:
        perm = db.query(Permission).filter(Permission.code == code).first()
        if perm:
            rp = RolePermission(role_id=doctor_role.id, permission_id=perm.id)
            db.add(rp)
    
    # Receptionist permissions
    for code in receptionist_perms:
        perm = db.query(Permission).filter(Permission.code == code).first()
        if perm:
            rp = RolePermission(role_id=receptionist_role.id, permission_id=perm.id)
            db.add(rp)
    
    db.commit()


def _setup_db():
    """Drop all tables, create them fresh, and seed required data."""
    from app.database import Base
    from app.database import engine
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Seed roles and permissions
    db = TestingSessionLocal()
    try:
        _seed_roles_and_permissions(db)
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    from app.database import Base
    from app.database import engine
    from app.main import app
    from app.routers import auth as auth_router
    from app.routers import patients as patients_router
    from app.routers import appointments as appointments_router
    from app.routers import treatments as treatments_router
    from app.routers import bills as bills_router
    from app.routers import dashboard as dashboard_router
    from app.routers import attachments as attachments_router
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    _setup_db()

    app.dependency_overrides[auth_router.get_db] = override_get_db
    app.dependency_overrides[patients_router.get_db] = override_get_db
    app.dependency_overrides[appointments_router.get_db] = override_get_db
    app.dependency_overrides[treatments_router.get_db] = override_get_db
    app.dependency_overrides[bills_router.get_db] = override_get_db
    app.dependency_overrides[dashboard_router.get_db] = override_get_db
    app.dependency_overrides[attachments_router.get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session():
    from app.database import Base
    from app.database import engine
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    _setup_db()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def signup_doctor(client, email, name="Test Doctor", clinic_name="Clinic A"):
    """
    Sign up a new doctor (creates org + admin user + doctor profile) and log them in.
    Returns (headers, doctor_profile_id) where headers includes Authorization and X-Organization-ID.
    """
    payload = {
        "name": name,
        "email": email,
        "password": "secret123",
        "role_code": "admin",
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 200, response.text

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert login_response.status_code == 200, login_response.text
    data = login_response.json()
    token = data["access_token"]
    user_data = data["user"]
    
    org_id = user_data["organization_id"]
    doctor_profile_id = user_data["doctor_profile_id"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org_id),
    }
    return headers, doctor_profile_id


def signup_doctor_full(client, email, name="Test Doctor", clinic_name="Clinic A"):
    """
    Sign up a new doctor and return full context.
    Returns (headers, org_id, doctor_profile_id).
    """
    headers, doctor_profile_id = signup_doctor(client, email, name, clinic_name)
    org_id = int(headers["X-Organization-ID"])
    return headers, org_id, doctor_profile_id


def create_user_in_org(client, headers, email, name, role_code="receptionist"):
    """Create a user in the current organization."""
    payload = {
        "email": email,
        "name": name,
        "password": "secret123",
        "role_code": role_code,
    }
    response = client.post("/users", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def login_user(client, email, password="secret123"):
    """Log in a user and return headers with their first org."""
    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    data = login_response.json()
    token = data["access_token"]
    user_data = data["user"]
    
    org_id = user_data["organization_id"]
    doctor_profile_id = user_data["doctor_profile_id"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org_id),
    }
    return headers, org_id, doctor_profile_id