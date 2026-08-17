from conftest import signup_doctor

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.models.bill import Bill


def test_doctor_cannot_access_or_modify_other_doctors_resources(client):
    headers_a, doctor_a_id = signup_doctor(client, "doctor_a_cross@example.com", "Doctor A", "Clinic A")
    headers_b, doctor_b_id = signup_doctor(client, "doctor_b_cross@example.com", "Doctor B", "Clinic B")

    patient_b = client.post(
        "/patients/",
        headers=headers_b,
        json={
            "name": "Other Doctor Patient",
            "phone": "2000000001",
            "email": "otherdoctorpatient@example.com",
            "age": 44,
            "gender": "female",
        },
    )
    assert patient_b.status_code == 200, patient_b.text
    patient_b_id = patient_b.json()["id"]

    appointment_b = client.post(
        "/appointments/",
        headers=headers_b,
        json={
            "patient_id": patient_b_id,
            "doctor_name": "Doctor B",
            "appointment_date": "2026-08-20",
            "status": "scheduled",
            "notes": "doctor b only",
        },
    )
    assert appointment_b.status_code == 200, appointment_b.text
    appointment_b_id = appointment_b.json()["id"]

    treatment_b = client.post(
        "/treatments/",
        headers=headers_b,
        json={
            "patient_id": patient_b_id,
            "treatment_name": "B-only Treatment",
            "cost": 220,
            "status": "pending",
            "notes": "doctor b only",
            "treatment_date": "2026-08-19T00:00:00Z",
        },
    )
    assert treatment_b.status_code == 200, treatment_b.text
    treatment_b_id = treatment_b.json()["id"]

    bill_b = client.post(
        "/bills/",
        headers=headers_b,
        json={
            "patient_id": patient_b_id,
            "amount": 310,
            "payment_status": "pending",
            "payment_method": "cash",
        },
    )
    assert bill_b.status_code == 200, bill_b.text
    bill_b_id = bill_b.json()["id"]

    access_checks = [
        (client.get, f"/patients/{patient_b_id}", headers_a, 404),
        (client.put, f"/patients/{patient_b_id}", headers_a, 404, {"name": "Should fail"}),
        (client.delete, f"/patients/{patient_b_id}", headers_a, 404),
        (client.put, f"/appointments/{appointment_b_id}", headers_a, 404, {"status": "completed"}),
        (client.delete, f"/appointments/{appointment_b_id}", headers_a, 404),
        (client.put, f"/treatments/{treatment_b_id}", headers_a, 404, {"status": "completed"}),
        (client.delete, f"/treatments/{treatment_b_id}", headers_a, 404),
        (client.put, f"/bills/{bill_b_id}", headers_a, 404, {"amount": 999}),
        (client.delete, f"/bills/{bill_b_id}", headers_a, 404),
    ]

    for call, path, auth_header, expected_status, *extra in access_checks:
        if extra:
            response = call(path, headers=auth_header, json=extra[0])
        else:
            response = call(path, headers=auth_header)
        assert response.status_code == expected_status, f"{path} expected {expected_status} but got {response.status_code}: {response.text}"

    assert client.get("/appointments/", headers=headers_a).json() == []
    assert client.get("/treatments/", headers=headers_a).json() == []
    assert client.get("/bills/", headers=headers_a).json() == []

    patient_create_payload = {
        "name": "Forged Patient",
        "phone": "2000000002",
        "email": "forged@example.com",
        "age": 42,
        "gender": "male",
        "doctor_id": doctor_b_id,
    }
    forged = client.post("/patients/", headers=headers_a, json=patient_create_payload)
    assert forged.status_code == 200, forged.text
    assert forged.json()["id"] is not None
    assert forged.json()["name"] == "Forged Patient"
    assert forged.json()["doctor_id"] == doctor_a_id if "doctor_id" in forged.json() else True

    appointment_forged = client.post(
        "/appointments/",
        headers=headers_a,
        json={
            "patient_id": forged.json()["id"],
            "doctor_name": "Doctor A",
            "appointment_date": "2026-08-21",
            "status": "pending",
            "doctor_id": doctor_b_id,
        },
    )
    assert appointment_forged.status_code == 200, appointment_forged.text
    assert appointment_forged.json()["doctor_id"] == doctor_a_id if "doctor_id" in appointment_forged.json() else True

    treatment_forged = client.post(
        "/treatments/",
        headers=headers_a,
        json={
            "patient_id": forged.json()["id"],
            "treatment_name": "Forged Treatment",
            "cost": 120,
            "status": "active",
            "treatment_date": "2026-08-21T00:00:00Z",
            "doctor_id": doctor_b_id,
        },
    )
    assert treatment_forged.status_code == 200, treatment_forged.text
    assert treatment_forged.json()["doctor_id"] == doctor_a_id if "doctor_id" in treatment_forged.json() else True

    bill_forged = client.post(
        "/bills/",
        headers=headers_a,
        json={
            "patient_id": forged.json()["id"],
            "amount": 150,
            "payment_status": "paid",
            "payment_method": "card",
            "doctor_id": doctor_b_id,
        },
    )
    assert bill_forged.status_code == 200, bill_forged.text
    assert bill_forged.json()["doctor_id"] == doctor_a_id if "doctor_id" in bill_forged.json() else True

    patient_update_forged = client.put(
        f"/patients/{forged.json()['id']}",
        headers=headers_a,
        json={"name": "Updated by A", "doctor_id": doctor_b_id},
    )
    assert patient_update_forged.status_code == 200, patient_update_forged.text
    assert patient_update_forged.json()["name"] == "Updated by A"

    appointment_update_forged = client.put(
        f"/appointments/{appointment_forged.json()['id']}",
        headers=headers_a,
        json={"status": "completed", "doctor_id": doctor_b_id},
    )
    assert appointment_update_forged.status_code == 200, appointment_update_forged.text
    assert appointment_update_forged.json()["status"] == "completed"

    treatment_update_forged = client.put(
        f"/treatments/{treatment_forged.json()['id']}",
        headers=headers_a,
        json={"status": "done", "doctor_id": doctor_b_id},
    )
    assert treatment_update_forged.status_code == 200, treatment_update_forged.text
    assert treatment_update_forged.json()["status"] == "done"

    bill_update_forged = client.put(
        f"/bills/{bill_forged.json()['id']}",
        headers=headers_a,
        json={"amount": 999, "doctor_id": doctor_b_id},
    )
    assert bill_update_forged.status_code == 200, bill_update_forged.text
    assert bill_update_forged.json()["amount"] == 999


def test_tenant_isolation_for_patients_appointments_treatments_and_bills(client, db_session):
    headers_a, doctor_a_id = signup_doctor(client, "doctor_a@example.com", "Doctor A", "Clinic A")
    headers_b, doctor_b_id = signup_doctor(client, "doctor_b@example.com", "Doctor B", "Clinic B")

    patient_a = client.post(
        "/patients/",
        headers=headers_a,
        json={
            "name": "Patient A",
            "phone": "1111111111",
            "email": "patienta@example.com",
            "age": 30,
            "gender": "female",
        },
    )
    assert patient_a.status_code == 200, patient_a.text
    patient_a_id = patient_a.json()["id"]

    patient_b = client.post(
        "/patients/",
        headers=headers_b,
        json={
            "name": "Patient B",
            "phone": "2222222222",
            "email": "patientb@example.com",
            "age": 40,
            "gender": "male",
        },
    )
    assert patient_b.status_code == 200, patient_b.text
    patient_b_id = patient_b.json()["id"]

    attack_patient_payload = {
        "name": "Hijack Patient",
        "phone": "3333333333",
        "email": "hijack@example.com",
        "age": 99,
        "gender": "other",
        "doctor_id": doctor_b_id,
    }
    hijack_patient = client.post(
        "/patients/",
        headers=headers_a,
        json=attack_patient_payload,
    )
    assert hijack_patient.status_code == 200, hijack_patient.text
    patient_from_db = db_session.query(Patient).filter(Patient.id == hijack_patient.json()["id"]).first()
    assert patient_from_db.doctor_id == doctor_a_id

    patient_lookup = client.get(f"/patients/{patient_b_id}", headers=headers_a)
    assert patient_lookup.status_code == 404, patient_lookup.text

    patient_update = client.put(
        f"/patients/{patient_b_id}",
        headers=headers_a,
        json={"name": "Hijacked Patient"},
    )
    assert patient_update.status_code == 404, patient_update.text

    appointment_b = client.post(
        "/appointments/",
        headers=headers_b,
        json={
            "patient_id": patient_b_id,
            "doctor_name": "Doctor B",
            "appointment_date": "2026-08-17",
            "status": "scheduled",
            "notes": "for doctor b",
        },
    )
    assert appointment_b.status_code == 200, appointment_b.text
    appointment_b_id = appointment_b.json()["id"]

    appointment_cross = client.post(
        "/appointments/",
        headers=headers_a,
        json={
            "patient_id": patient_b_id,
            "doctor_name": "Doctor A",
            "appointment_date": "2026-08-18",
            "status": "scheduled",
            "notes": "should fail",
        },
    )
    assert appointment_cross.status_code == 403, appointment_cross.text

    appointment_update = client.put(
        f"/appointments/{appointment_b_id}",
        headers=headers_a,
        json={"status": "completed"},
    )
    assert appointment_update.status_code == 404, appointment_update.text

    appointment_delete = client.delete(
        f"/appointments/{appointment_b_id}",
        headers=headers_a,
    )
    assert appointment_delete.status_code == 404, appointment_delete.text

    treatment_b = client.post(
        "/treatments/",
        headers=headers_b,
        json={
            "patient_id": patient_b_id,
            "treatment_name": "Treatment B",
            "cost": 200,
            "status": "active",
            "notes": "doctor b treatment",
            "treatment_date": "2026-08-16T00:00:00Z",
        },
    )
    assert treatment_b.status_code == 200, treatment_b.text
    treatment_b_id = treatment_b.json()["id"]

    treatment_cross = client.post(
        "/treatments/",
        headers=headers_a,
        json={
            "patient_id": patient_b_id,
            "treatment_name": "Attempted unauthorized treatment",
            "cost": 999,
            "status": "active",
            "notes": "should fail",
            "treatment_date": "2026-08-16T00:00:00Z",
        },
    )
    assert treatment_cross.status_code == 403, treatment_cross.text

    treatment_update = client.put(
        f"/treatments/{treatment_b_id}",
        headers=headers_a,
        json={"status": "completed"},
    )
    assert treatment_update.status_code == 404, treatment_update.text

    treatment_delete = client.delete(
        f"/treatments/{treatment_b_id}",
        headers=headers_a,
    )
    assert treatment_delete.status_code == 404, treatment_delete.text

    bill_b = client.post(
        "/bills/",
        headers=headers_b,
        json={
            "patient_id": patient_b_id,
            "amount": 500,
            "payment_status": "pending",
            "payment_method": "cash",
        },
    )
    assert bill_b.status_code == 200, bill_b.text
    bill_b_id = bill_b.json()["id"]

    bill_cross = client.post(
        "/bills/",
        headers=headers_a,
        json={
            "patient_id": patient_b_id,
            "amount": 999,
            "payment_status": "paid",
            "payment_method": "card",
        },
    )
    assert bill_cross.status_code == 403, bill_cross.text

    bill_update = client.put(
        f"/bills/{bill_b_id}",
        headers=headers_a,
        json={"amount": 777},
    )
    assert bill_update.status_code == 404, bill_update.text

    bill_delete = client.delete(
        f"/bills/{bill_b_id}",
        headers=headers_a,
    )
    assert bill_delete.status_code == 404, bill_delete.text

    assert client.get("/patients/", headers=headers_a).json()[-1]["id"] == patient_a_id
    assert client.get("/appointments/", headers=headers_a).json() == []
    assert client.get("/treatments/", headers=headers_a).json() == []
    assert client.get("/bills/", headers=headers_a).json() == []

    a_patient_record = db_session.query(Patient).filter(Patient.id == patient_a_id).first()
    b_patient_record = db_session.query(Patient).filter(Patient.id == patient_b_id).first()
    assert a_patient_record.doctor_id == doctor_a_id
    assert b_patient_record.doctor_id == doctor_b_id

    appointment_record = db_session.query(Appointment).filter(Appointment.id == appointment_b_id).first()
    treatment_record = db_session.query(Treatment).filter(Treatment.id == treatment_b_id).first()
    bill_record = db_session.query(Bill).filter(Bill.id == bill_b_id).first()
    assert appointment_record.doctor_id == doctor_b_id
    assert treatment_record.doctor_id == doctor_b_id
    assert bill_record.doctor_id == doctor_b_id
