from fastapi.testclient import TestClient

from app.main import app


def test_error_metrics_are_registered():
    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    assert "application_errors_total" in body
    assert "application_database_errors_total" in body
    assert "application_ai_service_errors_total" in body
    assert "application_unexpected_errors_total" in body
    assert "application_validation_errors_total" in body


def test_metrics_endpoint_exposes_error_metrics():
    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    assert "application_errors_total" in body
    assert "application_database_errors_total" in body
    assert "application_ai_service_errors_total" in body
    assert "application_unexpected_errors_total" in body
    assert "application_validation_errors_total" in body
