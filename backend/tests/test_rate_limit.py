import pytest

from conftest import signup_doctor

from app.ratelimit import AUTH_LIMITER
from app.ratelimit import IMPORT_LIMITER


@pytest.fixture(autouse=True)
def enable_rate_limiting(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    AUTH_LIMITER.reset()
    IMPORT_LIMITER.reset()


def test_signup_is_rate_limited_after_5_attempts(client):
    for attempt in range(5):
        response = client.post(
            "/auth/signup",
            json={
                "name": f"Rate Limit {attempt}",
                "email": f"ratelimit{attempt}@example.com",
                "password": "secret123",
                "role_code": "admin",
            },
        )
        assert response.status_code == 200, response.text

    response = client.post(
        "/auth/signup",
        json={
            "name": "Rate Limit 6",
            "email": "ratelimit6@example.com",
            "password": "secret123",
            "role_code": "admin",
        },
    )
    assert response.status_code == 429, response.text
    assert "Retry-After" in response.headers


def test_login_is_rate_limited_after_5_attempts(client):
    for _ in range(5):
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "wrong"},
        )
        assert response.status_code == 401, response.text

    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrong"},
    )
    assert response.status_code == 429, response.text
    assert "Retry-After" in response.headers
    assert int(response.headers["Retry-After"]) >= 1


def test_import_is_rate_limited_after_10_attempts(client):
    headers_a, _ = signup_doctor(client, "ratelimit_import@example.com", "Rate Limit Import", "Clinic")

    csv_content = "name,phone,email\nAlice,0130000001,rateimport@example.com\n"
    for _ in range(10):
        response = client.post(
            "/patients/import/preview",
            headers=headers_a,
            files={"file": ("patients.csv", csv_content, "text/csv")},
        )
        assert response.status_code == 200, response.text

    response = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 429, response.text
    assert "Retry-After" in response.headers


def test_rate_limited_request_returns_clear_message(client):
    for _ in range(5):
        client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "wrong"},
        )

    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrong"},
    )
    assert response.status_code == 429
    assert response.json()["detail"]