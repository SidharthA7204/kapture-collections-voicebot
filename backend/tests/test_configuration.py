import pytest

from app.core.config import Settings


def test_production_requires_vapi_api_key():
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            VAPI_API_KEY="",
            VAPI_ASSISTANT_ID="assistant-123",
            VAPI_WEBHOOK_SECRET="secret-123",
        )


def test_production_requires_vapi_assistant_id():
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            VAPI_API_KEY="api-key-123",
            VAPI_ASSISTANT_ID="",
            VAPI_WEBHOOK_SECRET="secret-123",
        )


def test_production_requires_vapi_webhook_secret():
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            VAPI_API_KEY="api-key-123",
            VAPI_ASSISTANT_ID="assistant-123",
            VAPI_WEBHOOK_SECRET="",
        )


def test_production_rejects_default_database_url():
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL=(
                "postgresql+psycopg://kapture_user:"
                "kapture_password@localhost:5432/kapture"
            ),
            VAPI_API_KEY="api-key-123",
            VAPI_ASSISTANT_ID="assistant-123",
            VAPI_WEBHOOK_SECRET="secret-123",
        )


def test_invalid_environment_is_rejected():
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="prod",
            DATABASE_URL=(
                "postgresql+psycopg://prod_user:"
                "strong_password@db.example.com:5432/kapture"
            ),
            VAPI_API_KEY="api-key-123",
            VAPI_ASSISTANT_ID="assistant-123",
            VAPI_WEBHOOK_SECRET="secret-123",
        )

def test_production_requires_groq_api_key():
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            GROQ_API_KEY="",
            VAPI_API_KEY="api-key-123",
            VAPI_ASSISTANT_ID="assistant-123",
            VAPI_WEBHOOK_SECRET="secret-123",
            DATABASE_URL=(
                "postgresql+psycopg://prod_user:"
                "strong_password@db.example.com:5432/kapture"
            ),
        )

def test_groq_timeout_must_be_positive():
    with pytest.raises(ValueError):
        Settings(
            GROQ_TIMEOUT_SECONDS=0,
        )


def test_groq_timeout_cannot_be_negative():
    with pytest.raises(ValueError):
        Settings(
            GROQ_TIMEOUT_SECONDS=-5,
        )

def test_invalid_log_level_is_rejected():
    with pytest.raises(ValueError):
        Settings(
            LOG_LEVEL="INVALID",
        )


def test_log_level_is_case_insensitive():
    configuration = Settings(
        LOG_LEVEL="warning",
    )

    assert configuration.LOG_LEVEL == "warning"
