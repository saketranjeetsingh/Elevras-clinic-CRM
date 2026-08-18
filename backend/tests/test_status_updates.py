from conftest import signup_doctor


def _create_patient(client, headers, phone, email):
    response = client.post(
        "/patients/",
        headers=headers,
        json={
            "name": "Status Test Patient",
            "phone": phone,
            "email": email,
            "age": 35,
            "gender": "female",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_appointment_status_update_via_body(client):
    headers, _ = signup_doctor(client, "status_appt@example.com")
    patient_id = _create_patient(client, headers, "9999990001", "status_appt_patient@example.com")

    created = client.post(
        "/appointments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_name": "Dr Status",
            "appointment_date": "2026-08-25",
            "status": "Scheduled",
            "notes": "status update test",
        },
    )
    assert created.status_code == 200, created.text
    appointment_id = created.json()["id"]
    assert created.json()["status"] == "Scheduled"

    updated = client.put(
        f"/appointments/{appointment_id}",
        headers=headers,
        json={"status": "Completed"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "Completed"

    listed = client.get("/appointments/", headers=headers).json()
    assert any(item["id"] == appointment_id and item["status"] == "Completed" for item in listed)


def test_treatment_status_update_via_body(client):
    headers, _ = signup_doctor(client, "status_treatment@example.com")
    patient_id = _create_patient(client, headers, "9999990002", "status_treatment_patient@example.com")

    created = client.post(
        "/treatments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "treatment_name": "Status Update Treatment",
            "cost": 150,
            "status": "Planned",
            "notes": "status update test",
        },
    )
    assert created.status_code == 200, created.text
    treatment_id = created.json()["id"]
    assert created.json()["status"] == "Planned"

    updated = client.put(
        f"/treatments/{treatment_id}",
        headers=headers,
        json={"status": "Completed"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "Completed"

    listed = client.get("/treatments/", headers=headers).json()
    assert any(item["id"] == treatment_id and item["status"] == "Completed" for item in listed)


def test_bill_payment_status_update_via_body(client):
    headers, _ = signup_doctor(client, "status_bill@example.com")
    patient_id = _create_patient(client, headers, "9999990003", "status_bill_patient@example.com")

    created = client.post(
        "/bills/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "amount": 250,
            "payment_status": "Pending",
            "payment_method": "Cash",
        },
    )
    assert created.status_code == 200, created.text
    bill_id = created.json()["id"]
    assert created.json()["payment_status"] == "Pending"

    updated = client.put(
        f"/bills/{bill_id}",
        headers=headers,
        json={"payment_status": "Paid"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["payment_status"] == "Paid"

    listed = client.get("/bills/", headers=headers).json()
    assert any(item["id"] == bill_id and item["payment_status"] == "Paid" for item in listed)
