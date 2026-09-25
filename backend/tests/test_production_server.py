from pathlib import Path


DOCKERFILE = (
    Path(__file__).resolve().parents[1]
    / "Dockerfile"
)


def test_production_server_uses_uvicorn():
    content = DOCKERFILE.read_text(
        encoding="utf-8"
    )

    assert '"uvicorn"' in content
    assert '"app.main:app"' in content


def test_production_server_binds_to_all_interfaces():
    content = DOCKERFILE.read_text(
        encoding="utf-8"
    )

    assert '"--host"' in content
    assert '"0.0.0.0"' in content


def test_production_server_uses_port_8000():
    content = DOCKERFILE.read_text(
        encoding="utf-8"
    )

    assert '"--port"' in content
    assert '"8000"' in content


def test_production_server_uses_multiple_workers():
    content = DOCKERFILE.read_text(
        encoding="utf-8"
    )

    assert '"--workers"' in content
    assert '"2"' in content


def test_production_server_has_keep_alive_timeout():
    content = DOCKERFILE.read_text(
        encoding="utf-8"
    )

    assert '"--timeout-keep-alive"' in content
    assert '"5"' in content
