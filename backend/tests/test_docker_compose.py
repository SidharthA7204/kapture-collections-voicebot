from pathlib import Path


COMPOSE_FILE = (
    Path(__file__).resolve().parents[2]
    / "docker-compose.yml"
)


def test_production_compose_file_exists():
    assert COMPOSE_FILE.exists()


def test_postgres_has_healthcheck():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert "postgres:" in content
    assert "pg_isready" in content
    assert "service_healthy" in content


def test_api_has_healthcheck():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert "api:" in content
    assert "localhost:8000/health" in content


def test_api_depends_on_healthy_postgres():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert "depends_on:" in content
    assert "condition: service_healthy" in content


def test_api_is_exposed_internally():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert "expose:" in content
    assert "8000" in content


def test_database_uses_internal_compose_hostname():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert (
        "postgresql+psycopg://"
        "kapture_user:kapture_password@"
        "postgres:5432/kapture"
    ) in content


def test_compose_does_not_use_host_database_routing():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert "host.docker.internal:5433" not in content

