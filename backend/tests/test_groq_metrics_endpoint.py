from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_metrics_endpoint_contains_groq_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    assert "groq_requests_total" in body
    assert "groq_request_duration_seconds" in body
    assert "groq_errors_total" in body
    assert "groq_timeouts_total" in body
    assert "groq_success_total" in body
