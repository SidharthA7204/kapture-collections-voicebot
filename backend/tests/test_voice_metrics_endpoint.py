from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_metrics_endpoint_contains_voice_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    assert "voice_calls_started_total" in body
    assert "voice_calls_completed_total" in body
    assert "voice_calls_active" in body
    assert "voice_call_duration_seconds" in body
    assert "voice_calls_ended_total" in body
