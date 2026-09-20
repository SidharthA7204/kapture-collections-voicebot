import logging

from app.core import logging as logging_module


def test_configure_logging_uses_configured_log_level(
    monkeypatch,
):
    captured = {}

    def fake_basic_config(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        logging,
        "basicConfig",
        fake_basic_config,
    )

    monkeypatch.setattr(
        logging_module.settings,
        "LOG_LEVEL",
        "DEBUG",
    )

    logging_module.configure_logging()

    assert captured["level"] == logging.DEBUG

def test_configure_logging_falls_back_to_info_for_invalid_log_level(
    monkeypatch,
):
    import logging

    from app.core import logging as logging_module

    captured = {}

    def fake_basic_config(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        logging,
        "basicConfig",
        fake_basic_config,
    )

    monkeypatch.setattr(
        logging_module.settings,
        "LOG_LEVEL",
        "INVALID_LEVEL",
    )

    logging_module.configure_logging()

    assert captured["level"] == logging.INFO
