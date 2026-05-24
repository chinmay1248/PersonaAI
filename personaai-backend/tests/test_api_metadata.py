from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck_reports_environment() -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"]


def test_metadata_reports_extension_capabilities() -> None:
    response = client.get("/v1/meta")

    assert response.status_code == 200
    payload = response.json()
    extension = payload["clients"]["browser_extension"]
    assert "web.whatsapp.com" in extension["supported_hosts"]
    assert "reply_suggestions" in extension["features"]
