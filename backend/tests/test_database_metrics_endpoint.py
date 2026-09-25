from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_exposes_database_metrics():
    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200

    metrics = response.text

    assert "db_connections_checked_out_total" in metrics
    assert "db_connections_checked_in_total" in metrics
    assert "db_connection_errors_total" in metrics
    assert "db_connections_in_use" in metrics
    assert "db_connection_pool_size" in metrics
