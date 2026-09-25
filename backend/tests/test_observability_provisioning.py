from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_prometheus_configuration_exists():
    prometheus_config = (
        PROJECT_ROOT
        / "monitoring"
        / "prometheus.yml"
    )

    assert prometheus_config.is_file()

    content = prometheus_config.read_text(
        encoding="utf-8"
    )

    assert 'job_name: "kapture-api"' in content
    assert "metrics_path: /metrics" in content
    assert "api:8000" in content


def test_grafana_provisioning_files_exist():
    datasource_config = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "datasources"
        / "prometheus.yml"
    )

    dashboard_provider_config = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "dashboards"
        / "kapture.yml"
    )

    dashboard_json = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "dashboards"
        / "kapture-collections-voicebot.json"
    )

    assert datasource_config.is_file()
    assert dashboard_provider_config.is_file()
    assert dashboard_json.is_file()


def test_grafana_datasource_points_to_prometheus():
    datasource_config = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "datasources"
        / "prometheus.yml"
    )

    content = datasource_config.read_text(
        encoding="utf-8"
    )

    assert "type: prometheus" in content
    assert "url: http://prometheus:9090" in content
    assert "isDefault: true" in content


def test_grafana_dashboard_provider_points_to_dashboard_directory():
    provider_config = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "dashboards"
        / "kapture.yml"
    )

    content = provider_config.read_text(
        encoding="utf-8"
    )

    assert "type: file" in content
    assert "folder: Kapture" in content
    assert "/var/lib/grafana/dashboards" in content


def test_dashboard_json_contains_expected_dashboard():
    dashboard_json = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "dashboards"
        / "kapture-collections-voicebot.json"
    )

    content = dashboard_json.read_text(
        encoding="utf-8"
    )

    assert "Kapture Collections Voicebot" in content
    assert "http_requests_total" in content
    assert "groq_requests_total" in content
    assert "application_errors_total" in content
    assert "health_check_failures_total" in content


