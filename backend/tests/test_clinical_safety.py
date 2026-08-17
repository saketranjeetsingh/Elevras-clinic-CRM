from conftest import signup_doctor


def test_patient_delete_with_related_records_is_blocked(client):
    headers_a, _ = signup_doctor(client, "clinic_a@example.com", "Doctor A", "Clinic A")

    patient = client.post(
        "/patients/",
        headers=headers_a,
        json={
            "name": "Clinical Patient",
            "phone": "5555555555",
            "email": "clinical@example.com",
            "age": 25,
            "gender": "female",
        },
    )
    assert patient.status_code == 200, patient.text
    patient_id = patient.json()["id"]

    appointment = client.post(
        "/appointments/",
        headers=headers_a,
        json={
            "patient_id": patient_id,
            "doctor_name": "Doctor A",
            "appointment_date": "2026-08-17",
            "status": "scheduled",
        },
    )
    assert appointment.status_code == 200, appointment.text

    treatment = client.post(
        "/treatments/",
        headers=headers_a,
        json={
            "patient_id": patient_id,
            "treatment_name": "Follow-up",
            "cost": 100,
            "status": "active",
            "treatment_date": "2026-08-15T00:00:00Z",
        },
    )
    assert treatment.status_code == 200, treatment.text

    bill = client.post(
        "/bills/",
        headers=headers_a,
        json={
            "patient_id": patient_id,
            "amount": 200,
            "payment_status": "pending",
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 200, bill.text

    delete_response = client.delete(f"/patients/{patient_id}", headers=headers_a)
    assert delete_response.status_code == 409, delete_response.text
    assert "Cannot delete patient" in delete_response.json()["detail"]

    remaining_patient = client.get(f"/patients/{patient_id}", headers=headers_a)
    assert remaining_patient.status_code == 200, remaining_patient.text

    appointments = client.get("/appointments/", headers=headers_a)
    assert len(appointments.json()) == 1
    treatments = client.get("/treatments/", headers=headers_a)
    assert len(treatments.json()) == 1
    bills = client.get("/bills/", headers=headers_a)
    assert len(bills.json()) == 1


def test_last_treatment_cannot_be_set_via_patient_input(client):
    headers_a, _ = signup_doctor(client, "clinic_b@example.com", "Doctor B", "Clinic B")

    patient = client.post(
        "/patients/",
        headers=headers_a,
        json={
            "name": "No Last Treatment",
            "phone": "7777777777",
            "email": "notlast@example.com",
            "age": 35,
            "gender": "male",
            "last_treatment": "Injected secret",
        },
    )
    assert patient.status_code == 200, patient.text
    assert patient.json().get("last_treatment") is None

    update = client.put(
        "/patients/" + str(patient.json()["id"]),
        headers=headers_a,
        json={"last_treatment": "Hacked field"},
    )
    assert update.status_code == 200, update.text
    assert update.json().get("last_treatment") is None
