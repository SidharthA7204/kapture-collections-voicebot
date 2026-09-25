from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NGINX_CONFIG = PROJECT_ROOT / "nginx" / "nginx.conf"
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


def read_nginx_config():
    return NGINX_CONFIG.read_text(
        encoding="utf-8"
    )


def test_nginx_hides_server_version():
    content = read_nginx_config()

    assert "server_tokens off;" in content


def test_nginx_sets_content_type_protection():
    content = read_nginx_config()

    assert (
        'X-Content-Type-Options "nosniff" always'
        in content
    )


def test_nginx_sets_clickjacking_protection():
    content = read_nginx_config()

    assert (
        'X-Frame-Options "DENY" always'
        in content
    )


def test_nginx_sets_referrer_policy():
    content = read_nginx_config()

    assert (
        'Referrer-Policy "strict-origin-when-cross-origin" always'
        in content
    )


def test_nginx_restricts_browser_permissions():
    content = read_nginx_config()

    assert (
        'Permissions-Policy "camera=(), microphone=(), geolocation=()" always'
        in content
    )


def test_api_port_remains_internal():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert '"8000:8000"' not in content
    assert "expose:" in content


def test_nginx_is_public_http_entrypoint():
    content = COMPOSE_FILE.read_text(
        encoding="utf-8"
    )

    assert '"80:80"' in content
