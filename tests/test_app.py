from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


def test_health_ok():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "gpu" in data


def test_ocr_stub_recognition_without_api_key():
    # Default is api-key mode but with no key set, should allow
    settings.auth_mode = "api-key"
    settings.api_key = None
    client = TestClient(app)
    files = {"file": ("hosts", b"127.0.0.1 localhost", "text/plain")}
    r = client.post("/ocr", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["result"]["text"] in ("stub", "", None)


def test_ocr_requires_api_key_when_set():
    settings.auth_mode = "api-key"
    settings.api_key = "secret"
    client = TestClient(app)
    files = {"file": ("hosts", b"127.0.0.1 localhost", "text/plain")}
    # Without header -> 401
    r = client.post("/ocr", files=files)
    assert r.status_code == 401
    # With header -> 200
    r2 = client.post("/ocr", files=files, headers={"x-api-key": "secret"})
    assert r2.status_code == 200


def test_structure_and_extraction_stubs():
    settings.auth_mode = "api-key"
    settings.api_key = None
    client = TestClient(app)
    files = {"file": ("hosts", b"127.0.0.1 localhost", "text/plain")}
    r1 = client.post("/structure", files=files)
    r2 = client.post("/extraction", files=files)
    assert r1.status_code == 200
    assert r2.status_code == 200
