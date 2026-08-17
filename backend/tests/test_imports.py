import io

from conftest import signup_doctor


def _csv_text(rows):
    lines = ["name,phone,email,age,gender,address,blood_group,medical_history,notes,last_treatment"]
    for row in rows:
        lines.append(",".join([str(value or "") for value in row]))
    return "\n".join(lines) + "\n"


def test_preview_requires_authentication(client):
    response = client.post(
        "/patients/import/preview",
        files={"file": ("patients.csv", "name,phone,email\nAlice,1234567890,alice@example.com\n", "text/csv")},
    )
    assert response.status_code == 401, response.text


def test_confirm_requires_authentication(client):
    response = client.post(
        "/patients/import/confirm",
        json={"rows": [{"name": "Alice", "phone": "1234567890", "email": "alice@example.com"}]},
    )
    assert response.status_code == 401, response.text


def test_valid_csv_preview_succeeds(client):
    headers_a, _ = signup_doctor(client, "import_preview@example.com", "Doctor Import", "Clinic Import")
    csv_content = "Name,Phone Number,Email Address,Age,Gender\nAlice,0123456789,alice@example.com,31,female\n"

    response = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_rows"] == 1
    assert data["valid_rows"] == 1
    assert data["invalid_rows"] == 0
    assert "name" in data["mapped_columns"].values()
    assert "phone" in data["mapped_columns"].values()
    assert data["unmapped_columns"] == []


def test_preview_does_not_create_database_records(client):
    headers_a, _ = signup_doctor(client, "preview_db@example.com", "Doctor Preview", "Clinic Preview")
    csv_content = "Patient Name,Mobile,Email Address\nPatient One,5550001111,patientone@example.com\n"

    preview = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert preview.status_code == 200, preview.text

    patient_list = client.get("/patients/", headers=headers_a)
    assert patient_list.status_code == 200, patient_list.text
    assert patient_list.json() == []


def test_valid_csv_confirmation_imports_patients_for_authenticated_doctor(client):
    headers_a, doctor_a_id = signup_doctor(client, "import_confirm@example.com", "Doctor Import Confirm", "Clinic Confirm")

    csv_content = "name,phone,email,age,gender\nAlice,0123000001,alice@example.com,31,female\nBob,0123000002,bob@example.com,32,male\n"
    preview = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert preview.status_code == 200, preview.text

    confirm = client.post(
        "/patients/import/confirm",
        headers=headers_a,
        json={"rows": preview.json()["preview_rows"]},
    )
    assert confirm.status_code == 200, confirm.text
    body = confirm.json()
    assert body["imported_count"] == 2
    assert body["skipped_duplicates"] == 0
    assert body["failed_validation"] == 0

    patient_list = client.get("/patients/", headers=headers_a)
    assert patient_list.status_code == 200, patient_list.text
    imported = patient_list.json()
    assert len(imported) == 2
    assert {p["doctor_id"] for p in imported} == {doctor_a_id}


def test_client_supplied_doctor_id_cannot_change_ownership(client):
    headers_a, doctor_a_id = signup_doctor(client, "doctor_ownership@example.com", "Doctor Ownership", "Clinic Ownership")

    payload = {
        "rows": [{
            "name": "Alice Ownership",
            "phone": "0999000001",
            "email": "ownership@example.com",
            "age": 40,
            "gender": "female",
            "doctor_id": 999,
        }]
    }

    response = client.post(
        "/patients/import/confirm",
        headers=headers_a,
        json=payload,
    )
    assert response.status_code == 200, response.text
    imported = client.get("/patients/", headers=headers_a).json()
    assert len(imported) == 1
    assert imported[0]["doctor_id"] == doctor_a_id


def test_doctor_a_cannot_affect_doctor_b_via_import(client):
    headers_a, _ = signup_doctor(client, "doctor_a_import@example.com", "Doctor A", "Clinic A")
    headers_b, _ = signup_doctor(client, "doctor_b_import@example.com", "Doctor B", "Clinic B")

    existing_b = client.post(
        "/patients/",
        headers=headers_b,
        json={
            "name": "Doctor B Patient",
            "phone": "1111111111",
            "email": "doctorbpatient@example.com",
            "age": 45,
            "gender": "male",
        },
    )
    assert existing_b.status_code == 200, existing_b.text
    patient_b_id = existing_b.json()["id"]

    preview = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", "name,phone,email\nDoctor B Patient,1111111111,doctorbpatient@example.com\n", "text/csv")},
    )
    assert preview.status_code == 200, preview.text
    assert len(preview.json()["duplicates"]) == 0, "Doctor A must NOT see Doctor B's patient as duplicate"

    confirm = client.post(
        "/patients/import/confirm",
        headers=headers_a,
        json={"rows": preview.json()["preview_rows"]},
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["imported_count"] == 1, "Doctor A must import successfully"
    assert confirm.json()["skipped_duplicates"] == 0

    patient_b_after = client.get(f"/patients/{patient_b_id}", headers=headers_b)
    assert patient_b_after.status_code == 200, patient_b_after.text
    assert patient_b_after.json()["email"] == "doctorbpatient@example.com"

    patient_a_list = client.get("/patients/", headers=headers_a)
    assert len(patient_a_list.json()) == 1, "Doctor A must have their own separate patient"
    assert patient_a_list.json()[0]["phone"] == "1111111111"


def test_duplicate_phone_and_email_are_reported(client):
    headers_a, _ = signup_doctor(client, "duplicate_import@example.com", "Doctor Duplicate", "Clinic Duplicate")

    existing = client.post(
        "/patients/",
        headers=headers_a,
        json={
            "name": "Existing Patient",
            "phone": "7777777777",
            "email": "existing@example.com",
            "age": 50,
            "gender": "female",
        },
    )
    assert existing.status_code == 200, existing.text

    csv_content = "name,phone,email\nNew Patient,7777777777,new@example.com\nAnother,8888888888,existing@example.com\n"
    response = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["duplicates"]) == 2, "Within same doctor, both rows must be detected as duplicates"


def test_existing_patient_is_not_overwritten(client):
    headers_a, _ = signup_doctor(client, "overwrite_import@example.com", "Doctor Overwrite", "Clinic Overwrite")

    existing = client.post(
        "/patients/",
        headers=headers_a,
        json={
            "name": "Existing Name",
            "phone": "4444444444",
            "email": "existingoverwrite@example.com",
            "age": 33,
            "gender": "unknown",
        },
    )
    assert existing.status_code == 200, existing.text

    preview = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", "name,phone,email\nExisting Name,4444444444,existingoverwrite@example.com\n", "text/csv")},
    )
    assert preview.status_code == 200, preview.text
    assert len(preview.json()["duplicates"]) >= 1

    confirm = client.post(
        "/patients/import/confirm",
        headers=headers_a,
        json={"rows": preview.json()["preview_rows"]},
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["imported_count"] == 0
    assert confirm.json()["skipped_duplicates"] >= 1

    current = client.get("/patients/", headers=headers_a)
    assert current.status_code == 200, current.text
    assert len(current.json()) == 1
    assert current.json()[0]["name"] == "Existing Name"


def test_invalid_rows_are_reported_individually(client):
    headers_a, _ = signup_doctor(client, "invalid_import@example.com", "Doctor Invalid", "Clinic Invalid")

    csv_content = "name,phone,email,age\nValid,0123000999,valid@example.com,30\nBad Name,,bad-email,abc\n"
    preview = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert preview.status_code == 200, preview.text
    data = preview.json()
    assert data["invalid_rows"] == 1
    assert len(data["errors"]) >= 1


def test_one_invalid_row_does_not_block_valid_rows(client):
    headers_a, _ = signup_doctor(client, "mixed_import@example.com", "Doctor Mixed", "Clinic Mixed")
    csv_content = "name,phone,email,age\nGood One,0123000111,goodone@example.com,20\nBad Row,,bad-email,abc\nAnother Good,0123000112,goodtwo@example.com,21\n"

    preview = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["valid_rows"] == 2
    assert preview.json()["invalid_rows"] == 1

    confirm = client.post(
        "/patients/import/confirm",
        headers=headers_a,
        json={"rows": preview.json()["preview_rows"]},
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["imported_count"] == 2


def test_empty_csv_is_handled_safely(client):
    headers_a, _ = signup_doctor(client, "empty_csv@example.com", "Doctor Empty", "Clinic Empty")

    response = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", "", "text/csv")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_rows"] == 0
    assert data["valid_rows"] == 0
    assert data["invalid_rows"] == 0
    assert data["preview_rows"] == []


def test_malformed_csv_is_handled_safely(client):
    headers_a, _ = signup_doctor(client, "malformed_csv@example.com", "Doctor Malformed", "Clinic Malformed")

    response = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", "name,phone\nAlice,0123000222\nBob\n", "text/csv")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_rows"] == 2
    assert data["invalid_rows"] >= 1


def test_unmapped_columns_are_reported(client):
    headers_a, _ = signup_doctor(client, "unmapped@example.com", "Doctor Unmapped", "Clinic Unmapped")
    csv_content = "Patient Name,Mobile,Insurance Number\nAlice,0123000333,ABC123\n"

    response = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "Insurance Number" in data["unmapped_columns"]


def test_phone_numbers_keep_leading_zeros(client):
    headers_a, _ = signup_doctor(client, "phone_zeros@example.com", "Doctor Phone", "Clinic Phone")
    csv_content = "name,phone,email\nZero Phone,0123400001,zeros@example.com\n"

    response = client.post(
        "/patients/import/preview",
        headers=headers_a,
        files={"file": ("patients.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200, response.text
    row = response.json()["preview_rows"][0]
    assert row["phone"] == "0123400001"
