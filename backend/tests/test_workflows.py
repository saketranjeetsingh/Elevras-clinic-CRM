from conftest import signup_doctor


def _create_patient(client, headers, phone, email, name="Workflow Patient"):
    response = client.post(
        "/patients/",
        headers=headers,
        json={
            "name": name,
            "phone": phone,
            "email": email,
            "date_of_birth": "1984-01-01T00:00:00Z",
            "gender": "female",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_patient_profile_returns_scoped_history_and_stats(client):
    headers, doctor_profile_id = signup_doctor(client, "profile_a@example.com", "Doctor A", "Clinic A")
    patient_id = _create_patient(client, headers, "9100000001", "profilepatient@example.com")

    appointment = client.post(
        "/appointments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "doctor_name": "Doctor A",
            "start_at": "2026-09-10T09:00:00Z",
            "end_at": "2026-09-10T09:30:00Z",
            "status": "Scheduled",
            "notes": "profile appointment",
        },
    )
    assert appointment.status_code == 200, appointment.text

    treatment = client.post(
        "/treatments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "treatment_name": "Root Canal",
            "cost": 300,
            "status": "In Progress",
            "notes": "profile treatment",
        },
    )
    assert treatment.status_code == 200, treatment.text

    bill = client.post(
        "/bills/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "amount": 250,
            "payment_status": "Pending",
            "payment_method": "Cash",
        },
    )
    assert bill.status_code == 200, bill.text

    profile = client.get(f"/patients/{patient_id}/profile", headers=headers)
    assert profile.status_code == 200, profile.text
    data = profile.json()

    assert data["patient"]["id"] == patient_id
    assert len(data["appointments"]) == 1
    assert len(data["treatments"]) == 1
    assert len(data["bills"]) == 1
    assert data["stats"]["pending_amount"] == 250
    assert data["stats"]["last_treatment"] == "Root Canal"

    treatment_payload = data["treatments"][0]
    assert treatment_payload["doctor_name"] == "Doctor A"
    assert treatment_payload["treatment_name"] == "Root Canal"
    assert "_sa_instance_state" not in treatment_payload


def test_appointment_partial_update_preserves_other_fields(client):
    headers, doctor_profile_id = signup_doctor(client, "appt_partial@example.com")
    patient_id = _create_patient(client, headers, "9100000002", "apptpartial@example.com")

    created = client.post(
        "/appointments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "doctor_name": "Dr Partial",
            "start_at": "2026-09-15T09:00:00Z",
            "end_at": "2026-09-15T09:30:00Z",
            "status": "Scheduled",
            "notes": "keep these notes",
        },
    )
    assert created.status_code == 200, created.text
    appointment_id = created.json()["id"]

    updated = client.put(
        f"/appointments/{appointment_id}",
        headers=headers,
        json={"status": "Completed"},
    )
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["status"] == "Completed"
    assert body["notes"] == "keep these notes"
    # Compare datetime values (allow different timezone representations)
    from datetime import datetime
    expected_start = datetime.fromisoformat("2026-09-15T09:00:00+00:00")
    actual_start = datetime.fromisoformat(body["start_at"])
    assert actual_start == expected_start
    assert body["doctor_name"] == "Dr Partial"
    assert body["patient_id"] == patient_id

    listed = client.get("/appointments/", headers=headers).json()
    persisted = next(item for item in listed if item["id"] == appointment_id)
    assert persisted["status"] == "Completed"
    assert persisted["notes"] == "keep these notes"

    deleted = client.delete(f"/appointments/{appointment_id}", headers=headers)
    assert deleted.status_code == 200, deleted.text

    second_delete = client.delete(f"/appointments/{appointment_id}", headers=headers)
    assert second_delete.status_code == 404, second_delete.text

    remaining = client.get("/appointments/", headers=headers).json()
    assert all(item["id"] != appointment_id for item in remaining)


def test_treatment_create_update_delete(client):
    headers, doctor_profile_id = signup_doctor(client, "treatment_flow@example.com")
    patient_id = _create_patient(client, headers, "9100000003", "treatmentflow@example.com")

    created = client.post(
        "/treatments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "treatment_name": "Scaling",
            "cost": 150,
            "status": "Planned",
            "notes": "before update",
        },
    )
    assert created.status_code == 200, created.text
    treatment_id = created.json()["id"]

    updated = client.put(
        f"/treatments/{treatment_id}",
        headers=headers,
        json={"status": "Completed"},
    )
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["status"] == "Completed"
    assert body["treatment_name"] == "Scaling"
    assert body["cost"] == 150
    assert body["notes"] == "before update"
    assert body["patient_id"] == patient_id

    listed = client.get("/treatments/", headers=headers).json()
    persisted = next(item for item in listed if item["id"] == treatment_id)
    assert persisted["status"] == "Completed"
    assert persisted["notes"] == "before update"

    deleted = client.delete(f"/treatments/{treatment_id}", headers=headers)
    assert deleted.status_code == 200, deleted.text
    assert client.delete(f"/treatments/{treatment_id}", headers=headers).status_code == 404


def test_bill_create_update_delete(client):
    headers, doctor_profile_id = signup_doctor(client, "bill_flow@example.com")
    patient_id = _create_patient(client, headers, "9100000004", "billflow@example.com")

    created = client.post(
        "/bills/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "amount": 500,
            "payment_status": "Pending",
            "payment_method": "Card",
        },
    )
    assert created.status_code == 200, created.text
    bill_id = created.json()["id"]

    updated = client.put(
        f"/bills/{bill_id}",
        headers=headers,
        json={"payment_status": "Paid"},
    )
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["payment_status"] == "Paid"
    assert body["amount"] == 500
    assert body["payment_method"] == "Card"
    assert body["patient_id"] == patient_id

    listed = client.get("/bills/", headers=headers).json()
    persisted = next(item for item in listed if item["id"] == bill_id)
    assert persisted["payment_status"] == "Paid"
    assert persisted["amount"] == 500

    deleted = client.delete(f"/bills/{bill_id}", headers=headers)
    assert deleted.status_code == 200, deleted.text
    assert client.delete(f"/bills/{bill_id}", headers=headers).status_code == 404


def test_patient_profile_is_tenant_scoped(client):
    headers_a, _ = signup_doctor(client, "profile_ten_a@example.com", "Doctor A", "Clinic A")
    headers_b, _ = signup_doctor(client, "profile_ten_b@example.com", "Doctor B", "Clinic B")

    patient_b = client.post(
        "/patients/",
        headers=headers_b,
        json={
            "name": "Tenant B Patient",
            "phone": "9100000005",
            "email": "tenantb@example.com",
            "date_of_birth": "1991-01-01T00:00:00Z",
            "gender": "male",
        },
    )
    assert patient_b.status_code == 200, patient_b.text
    patient_b_id = patient_b.json()["id"]

    cross = client.get(f"/patients/{patient_b_id}/profile", headers=headers_a)
    assert cross.status_code == 404, cross.text

    own = client.get(f"/patients/{patient_b_id}/profile", headers=headers_b)
    assert own.status_code == 200, own.text


def test_get_patients_supports_pagination(client):
    headers, _ = signup_doctor(client, "pagination@example.com", "Doctor Pagination", "Clinic")

    for index in range(3):
        _create_patient(client, headers, f"620000000{index}", f"pag{index}@example.com", f"Patient {index}")

    full = client.get("/patients/", headers=headers)
    assert full.status_code == 200, full.text
    assert len(full.json()) == 3

    first_page = client.get("/patients/?limit=2", headers=headers)
    assert first_page.status_code == 200, first_page.text
    assert len(first_page.json()) == 2

    second_page = client.get("/patients/?limit=2&skip=2", headers=headers)
    assert second_page.status_code == 200, second_page.text
    assert len(second_page.json()) == 1

    invalid = client.get("/patients/?limit=0", headers=headers)
    assert invalid.status_code == 422, invalid.text


def test_get_patients_derives_latest_treatment_name(client):
    headers, doctor_profile_id = signup_doctor(client, "lasttx_list@example.com", "Doctor List", "Clinic")

    patient_id = _create_patient(client, headers, "6200000100", "lasttxlist@example.com", "Patient List")

    first = client.post(
        "/treatments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "treatment_name": "Old Treatment",
            "cost": 100,
            "status": "Completed",
            "treatment_date": "2026-07-01T00:00:00Z",
        },
    )
    assert first.status_code == 200, first.text

    second = client.post(
        "/treatments/",
        headers=headers,
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_profile_id,
            "treatment_name": "New Treatment",
            "cost": 200,
            "status": "Planned",
            "treatment_date": "2026-08-01T00:00:00Z",
        },
    )
    assert second.status_code == 200, second.text

    patient_list = client.get("/patients/", headers=headers)
    assert patient_list.status_code == 200, patient_list.text
    assert patient_list.json()[0]["last_treatment"] == "New Treatment"


def test_health_endpoint_reports_database_status(client):
    response = client.get("/health")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"


def test_patients_without_email_can_be_created(client):
    headers, _ = signup_doctor(client, "no_email@example.com", "Doctor No Email", "Clinic No Email")

    first = client.post(
        "/patients/",
        headers=headers,
        json={
            "name": "First Caller",
            "phone": "6900000001",
        },
    )
    assert first.status_code == 200, first.text
    assert first.json()["email"] is None

    second = client.post(
        "/patients/",
        headers=headers,
        json={
            "name": "Second Caller",
            "phone": "6900000002",
        },
    )
    assert second.status_code == 200, second.text

    listed = client.get("/patients/", headers=headers)
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 2