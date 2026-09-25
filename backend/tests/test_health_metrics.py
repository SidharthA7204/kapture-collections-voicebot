from fastapi.testclient import TestClient

from app.core.health_metrics import (
    HEALTH_CHECKS_TOTAL,
    HEALTH_CHECK_FAILURES_TOTAL,
    READINESS_CHECKS_TOTAL,
    READINESS_CHECK_FAILURES_TOTAL,
)
from app.main import app


def test_health_metrics_are_registered():
    assert HEALTH_CHECKS_TOTAL is not None
    assert HEALTH_CHECK_FAILURES_TOTAL is not None
    assert READINESS_CHECKS_TOTAL is not None
    assert READINESS_CHECK_FAILURES_TOTAL is not None


def test_health_and_readiness_metrics_are_exposed():
    with TestClient(app) as client:
        client.get("/health")
        client.get("/ready")

        response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    assert "health_checks_total" in body
    assert "health_check_failures_total" in body
    assert "readiness_checks_total" in body
    assert "readiness_check_failures_total" in body
