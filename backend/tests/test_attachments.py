import os
import shutil
import tempfile

import pytest

from conftest import signup_doctor


@pytest.fixture(scope="function", autouse=True)
def upload_dir():
    temp_dir = tempfile.mkdtemp(prefix="elevras_uploads_")
    os.environ["UPLOAD_DIR"] = temp_dir
    yield temp_dir
    os.environ.pop("UPLOAD_DIR", None)
    shutil.rmtree(temp_dir, ignore_errors=True)


def _create_patient(client, headers, phone, email):
    response = client.post(
        "/patients/",
        headers=headers,
        json={
            "name": "Attachment Patient",
            "phone": phone,
            "email": email,
            "date_of_birth": "1989-01-01T00:00:00Z",
            "gender": "female",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def _upload(client, headers, patient_id, filename="xray.jpg", content_type="image/jpeg", data=b"fake-image-bytes"):
    return client.post(
        f"/patients/{patient_id}/attachments",
        headers=headers,
        data={"category": "x-ray", "notes": "recent scan"},
        files={"file": (filename, data, content_type)},
    )


def test_upload_requires_authentication(client):
    response = client.post(
        "/patients/1/attachments",
        files={"file": ("xray.jpg", b"data", "image/jpeg")},
    )
    assert response.status_code == 401, response.text


def test_download_requires_authentication(client):
    response = client.get("/attachments/1/file")
    assert response.status_code == 401, response.text


def test_upload_returns_metadata_and_writes_file(client, upload_dir):
    headers, doctor_profile_id = signup_doctor(client, "attach_upload@example.com", "Doctor Upload", "Clinic A")
    patient_id = _create_patient(client, headers, "7000000001", "attachedupload@example.com")

    response = _upload(client, headers, patient_id)
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["filename"] == "xray.jpg"
    assert body["content_type"] == "image/jpeg"
    assert body["category"] == "x-ray"
    assert body["notes"] == "recent scan"
    assert body["size"] == len(b"fake-image-bytes")
    assert body["patient_id"] == patient_id

    doctor_dir = os.path.join(upload_dir, "1", str(patient_id))
    assert os.path.isdir(doctor_dir)
    files = os.listdir(doctor_dir)
    assert len(files) == 1
    assert files[0].endswith(".jpg")


def test_upload_rejects_unsupported_type(client, upload_dir):
    headers, _ = signup_doctor(client, "attach_type@example.com", "Doctor Type", "Clinic A")
    patient_id = _create_patient(client, headers, "7000000002", "attachedtype@example.com")

    response = _upload(client, headers, patient_id, filename="notes.txt", content_type="text/plain")
    assert response.status_code == 415, response.text


def test_list_only_returns_own_doctors_files(client, upload_dir):
    headers_a, _ = signup_doctor(client, "attach_list_a@example.com", "Doctor A", "Clinic A")
    headers_b, _ = signup_doctor(client, "attach_list_b@example.com", "Doctor B", "Clinic B")

    patient_a = _create_patient(client, headers_a, "7000000010", "attachedlista@example.com")
    patient_b = _create_patient(client, headers_b, "7000000011", "attachedlistb@example.com")

    assert _upload(client, headers_a, patient_a).status_code == 200
    assert _upload(client, headers_a, patient_a, filename="second.jpg").status_code == 200
    assert _upload(client, headers_b, patient_b, filename="other.jpg").status_code == 200

    list_a = client.get(f"/patients/{patient_a}/attachments", headers=headers_a)
    assert list_a.status_code == 200, list_a.text
    assert len(list_a.json()) == 2

    cross = client.get(f"/patients/{patient_b}/attachments", headers=headers_a)
    assert cross.status_code in (403, 404), cross.text


def test_delete_is_tenant_scoped_and_removes_file(client, upload_dir):
    headers_a, doctor_a_id = signup_doctor(client, "attach_del_a@example.com", "Doctor A", "Clinic A")
    headers_b, _ = signup_doctor(client, "attach_del_b@example.com", "Doctor B", "Clinic B")

    patient_a = _create_patient(client, headers_a, "7000000020", "attacheddela@example.com")
    patient_b = _create_patient(client, headers_b, "7000000021", "attacheddelb@example.com")

    upload_a = _upload(client, headers_a, patient_a)
    assert upload_a.status_code == 200
    attachment_a_id = upload_a.json()["id"]

    upload_b = _upload(client, headers_b, patient_b)
    assert upload_b.status_code == 200
    attachment_b_id = upload_b.json()["id"]

    cross_delete = client.delete(
        f"/patients/{patient_a}/attachments/{attachment_b_id}",
        headers=headers_a,
    )
    assert cross_delete.status_code == 404, cross_delete.text

    wrong_doctor_delete = client.delete(
        f"/patients/{patient_b}/attachments/{attachment_b_id}",
        headers=headers_a,
    )
    assert wrong_doctor_delete.status_code == 404, wrong_doctor_delete.text

    delete = client.delete(
        f"/patients/{patient_a}/attachments/{attachment_a_id}",
        headers=headers_a,
    )
    assert delete.status_code == 200, delete.text

    remaining = client.get(f"/patients/{patient_a}/attachments", headers=headers_a).json()
    assert remaining == []

    doctor_dir = os.path.join(upload_dir, str(doctor_a_id), str(patient_a))
    assert not os.path.exists(doctor_dir) or os.listdir(doctor_dir) == []


def test_download_returns_bytes_with_media_type(client, upload_dir):
    headers, _ = signup_doctor(client, "attach_dl@example.com", "Doctor Download", "Clinic A")
    patient_id = _create_patient(client, headers, "7000000030", "attacheddl@example.com")

    payload = b"\x89PNG\r\n\x1a\nfake-png-content"
    upload = client.post(
        f"/patients/{patient_id}/attachments",
        headers=headers,
        files={"file": ("scan.png", payload, "image/png")},
    )
    assert upload.status_code == 200, upload.text
    attachment_id = upload.json()["id"]

    download = client.get(f"/attachments/{attachment_id}/file", headers=headers)
    assert download.status_code == 200, download.text
    assert download.headers["content-type"] == "image/png"
    assert download.content == payload

    cross_download = client.get(f"/attachments/{attachment_id}/file", headers=headers)
    assert cross_download.status_code == 200


def test_download_is_tenant_scoped(client, upload_dir):
    headers_a, _ = signup_doctor(client, "attach_dl_a@example.com", "Doctor A", "Clinic A")
    headers_b, _ = signup_doctor(client, "attach_dl_b@example.com", "Doctor B", "Clinic B")

    patient_a = _create_patient(client, headers_a, "7000000040", "attacheddla@example.com")
    upload = _upload(client, headers_a, patient_a)
    attachment_id = upload.json()["id"]

    cross = client.get(f"/attachments/{attachment_id}/file", headers=headers_b)
    assert cross.status_code == 404, cross.text

    missing = client.get("/attachments/99999/file", headers=headers_a)
    assert missing.status_code == 404, missing.text