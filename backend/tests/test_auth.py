from conftest import signup_doctor


def test_signup_login_and_me(client):
    payload = {
        "name": "Dr. Alice",
        "email": "alice@example.com",
        "password": "secret123",
        "clinic_name": "Alice Clinic",
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 200, response.text

    login_response = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["email"] == payload["email"]


def test_unauthenticated_access_is_rejected(client):
    response = client.get("/patients/")
    assert response.status_code == 401, response.text

    response = client.get("/dashboard/stats")
    assert response.status_code == 401, response.text
