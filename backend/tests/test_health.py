from fastapi.testclient import TestClient

from app.main import app


def test_health_check():

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "kapture-collections-backend"
    assert data["database"] == "healthy"
def test_readiness_check():
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["service"] == "kapture-collections-backend"
    assert data["database"] == "healthy"


def test_readiness_check_returns_503_when_database_is_unhealthy(
    monkeypatch,
):
    def fail_connection():
        raise RuntimeError(
            "database password=super-secret"
        )

    monkeypatch.setattr(
        "app.main.engine.connect",
        fail_connection,
    )

    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["service"] == "kapture-collections-backend"
    assert data["database"] == "unhealthy"

    assert "super-secret" not in response.text
    assert "password" not in response.text

def test_readiness_check():
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["service"] == "kapture-collections-backend"
    assert data["database"] == "healthy"


def test_readiness_check_returns_503_when_database_is_unhealthy(
    monkeypatch,
):
    def fail_connection():
        raise RuntimeError(
            "database password=super-secret"
        )

    monkeypatch.setattr(
        "app.main.engine.connect",
        fail_connection,
    )

    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["service"] == "kapture-collections-backend"
    assert data["database"] == "unhealthy"

    assert "super-secret" not in response.text
    assert "password" not in response.text
