from conftest import signup_doctor


def test_dashboard_statistics_are_scoped_to_current_doctor(client):
    headers_a, doctor_a_id = signup_doctor(client, "dash_a@example.com", "Doctor A", "Clinic A")
    headers_b, doctor_b_id = signup_doctor(client, "dash_b@example.com", "Doctor B", "Clinic B")

    patient_a = client.post(
        "/patients/",
        headers=headers_a,
        json={
            "name": "Dashboard Patient A",
            "phone": "1111111112",
            "email": "dashpatienta@example.com",
            "age": 31,
            "gender": "female",
        },
    )
    patient_b = client.post(
        "/patients/",
        headers=headers_b,
        json={
            "name": "Dashboard Patient B",
            "phone": "1111111113",
            "email": "dashpatientb@example.com",
            "age": 32,
            "gender": "male",
        },
    )
    assert patient_a.status_code == 200, patient_a.text
    assert patient_b.status_code == 200, patient_b.text

    client.post(
        "/appointments/",
        headers=headers_a,
        json={
            "patient_id": patient_a.json()["id"],
            "doctor_name": "Doctor A",
            "appointment_date": "2026-08-17",
            "status": "completed",
        },
    )
    client.post(
        "/appointments/",
        headers=headers_b,
        json={
            "patient_id": patient_b.json()["id"],
            "doctor_name": "Doctor B",
            "appointment_date": "2026-08-18",
            "status": "Scheduled",
        },
    )

    client.post(
        "/treatments/",
        headers=headers_a,
        json={
            "patient_id": patient_a.json()["id"],
            "treatment_name": "A Treatment",
            "cost": 150,
            "status": "done",
            "treatment_date": "2026-08-15T00:00:00Z",
        },
    )
    client.post(
        "/treatments/",
        headers=headers_b,
        json={
            "patient_id": patient_b.json()["id"],
            "treatment_name": "B Treatment",
            "cost": 300,
            "status": "done",
            "treatment_date": "2026-08-16T00:00:00Z",
        },
    )

    client.post(
        "/bills/",
        headers=headers_a,
        json={
            "patient_id": patient_a.json()["id"],
            "amount": 250,
            "payment_status": "paid",
            "payment_method": "card",
        },
    )
    client.post(
        "/bills/",
        headers=headers_b,
        json={
            "patient_id": patient_b.json()["id"],
            "amount": 400,
            "payment_status": "pending",
            "payment_method": "cash",
        },
    )

    dashboard_a = client.get("/dashboard/stats", headers=headers_a)
    dashboard_b = client.get("/dashboard/stats", headers=headers_b)

    assert dashboard_a.status_code == 200, dashboard_a.text
    assert dashboard_b.status_code == 200, dashboard_b.text

    assert dashboard_a.json()["total_patients"] == 1
    assert dashboard_a.json()["total_appointments"] == 1
    assert dashboard_a.json()["total_treatments"] == 1
    assert dashboard_a.json()["total_bills"] == 1
    assert dashboard_a.json()["paid_bills"] == 1
    assert dashboard_a.json()["pending_bills"] == 0
    assert dashboard_a.json()["total_revenue"] == 250
    assert dashboard_a.json()["pending_revenue"] == 0

    assert dashboard_b.json()["total_patients"] == 1
    assert dashboard_b.json()["total_appointments"] == 1
    assert dashboard_b.json()["total_treatments"] == 1
    assert dashboard_b.json()["total_bills"] == 1
    assert dashboard_b.json()["paid_bills"] == 0
    assert dashboard_b.json()["pending_bills"] == 1
    assert dashboard_b.json()["total_revenue"] == 0
    assert dashboard_b.json()["pending_revenue"] == 400
