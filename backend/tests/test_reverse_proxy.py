from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
NGINX_CONFIG = PROJECT_ROOT / "nginx" / "nginx.conf"


def test_nginx_config_exists():
    assert NGINX_CONFIG.exists()


def test_nginx_proxies_to_api():
    content = NGINX_CONFIG.read_text(
        encoding="utf-8"
    )

    assert "proxy_pass http://api:8000;" in content


def test_nginx_forwards_proxy_headers():
    content = NGINX_CONFIG.read_text(
        encoding="utf-8"
    )

    assert "X-Real-IP" in content
    assert "X-Forwarded-For" in content
    assert "X-Forwarded-Proto" in content


def test_nginx_has_request_size_limit():
    content = NGINX_CONFIG.read_text(
        encoding="utf-8"
    )

    assert "client_max_body_size 10m;" in content


def test_compose_exposes_nginx_port():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert '"80:80"' in content


def test_compose_does_not_publish_api_port():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert '"8000:8000"' not in content


def test_compose_mounts_nginx_configuration():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert "./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro" in content
