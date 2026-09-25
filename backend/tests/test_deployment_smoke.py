from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


def run_compose(*args):
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(COMPOSE_FILE),
            *args,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout


def test_postgres_container_is_healthy():
    output = run_compose(
        "ps",
        "--format",
        "json",
    )

    assert "kapture_postgres" in output
    assert "healthy" in output


def test_api_container_is_healthy():
    output = run_compose(
        "ps",
        "--format",
        "json",
    )

    assert "kapture_backend" in output
    assert "healthy" in output


def test_nginx_container_is_running():
    output = run_compose(
        "ps",
        "--format",
        "json",
    )

    assert "kapture_nginx" in output
    assert '"State":"running"' in output


def test_api_port_is_not_published():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert '"8000:8000"' not in content
    assert "expose:" in content


def test_nginx_port_is_published():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert '"80:80"' in content


def test_nginx_can_reach_api():
    result = subprocess.run(
        [
            "docker",
            "exec",
            "kapture_nginx",
            "wget",
            "-qO-",
            "http://api:8000/health",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert '"status":"healthy"' in result.stdout


def test_api_can_reach_database():
    result = subprocess.run(
        [
            "docker",
            "exec",
            "kapture_backend",
            "python",
            "-c",
            (
                "from sqlalchemy import text; "
                "from app.db.database import engine; "
                "print(engine.connect().execute("
                "text('SELECT 1')).scalar())"
            ),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "1" in result.stdout
