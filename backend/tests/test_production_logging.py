from pathlib import Path


LOGGING_FILE = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "core"
    / "logging.py"
)


def read_logging_config():
    return LOGGING_FILE.read_text(
        encoding="utf-8"
    )


def test_structured_logging_uses_json_renderer():
    content = read_logging_config()

    assert "JSONRenderer" in content


def test_structured_logging_includes_log_level():
    content = read_logging_config()

    assert "add_log_level" in content


def test_structured_logging_includes_timestamp():
    content = read_logging_config()

    assert "TimeStamper" in content
    assert 'fmt="iso"' in content


def test_structured_logging_merges_context():
    content = read_logging_config()

    assert "merge_contextvars" in content


def test_logging_uses_configured_log_level():
    content = read_logging_config()

    assert "settings.LOG_LEVEL.upper()" in content
