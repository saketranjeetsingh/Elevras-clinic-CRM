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

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

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
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def signup_doctor(client, email, name="Test Doctor", clinic_name="Clinic A"):
    payload = {
        "name": name,
        "email": email,
        "password": "secret123",
        "clinic_name": clinic_name,
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 200, response.text

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    doctor_id = me.json()["doctor_id"]
    return headers, doctor_id
