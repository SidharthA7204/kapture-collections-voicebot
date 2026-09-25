from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_returns_prometheus_data():
    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
    assert "http_requests_in_progress" in response.text
from fastapi.testclient import TestClient

from app.main import app


def test_request_metrics_record_http_request():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200

        metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200

    metrics = metrics_response.text

    assert 'http_requests_total{method="GET",path="/health",status="200"}' in metrics
    assert 'http_request_duration_seconds_count{method="GET",path="/health"}' in metrics
from fastapi.testclient import TestClient

from app.main import app


def test_failed_request_records_500_metric():
    @app.get("/test-metrics-error")
    async def test_metrics_error():
        raise RuntimeError("metrics test failure")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test-metrics-error")
        assert response.status_code == 500

        metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200

    metrics = metrics_response.text

    assert (
        'http_requests_total{method="GET",path="/test-metrics-error",status="500"}'
        in metrics
    )

    assert (
        'http_request_duration_seconds_count{method="GET",path="/test-metrics-error"}'
        in metrics
    )
from fastapi.testclient import TestClient

from app.core.metrics import HTTP_REQUESTS_IN_PROGRESS
from app.main import app


def test_in_progress_gauge_returns_to_zero():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200

        assert HTTP_REQUESTS_IN_PROGRESS._value.get() == 0
