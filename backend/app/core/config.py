from pydantic import model_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    APP_NAME: str = (
        "Kapture Finance AI Collections Voice Agent"
    )
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = (
        "postgresql+psycopg://kapture_user:"
        "kapture_password@localhost:5432/kapture"
    )

    LOG_LEVEL: str = "INFO"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TIMEOUT_SECONDS: float = 30.0

    VAPI_API_KEY: str = ""
    VAPI_ASSISTANT_ID: str = ""
    VAPI_WEBHOOK_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT.lower() == "production":
            required = {
                "GROQ_API_KEY": self.GROQ_API_KEY,
                "VAPI_API_KEY": self.VAPI_API_KEY,
                "VAPI_ASSISTANT_ID": self.VAPI_ASSISTANT_ID,
                "VAPI_WEBHOOK_SECRET": self.VAPI_WEBHOOK_SECRET,
            }

            missing = [
                name
                for name, value in required.items()
                if not value or not value.strip()
            ]

            if missing:
                raise ValueError(
                    "Missing required production "
                    f"configuration: {', '.join(missing)}"
                )

            default_database_url = (
                "postgresql+psycopg://kapture_user:"
                "kapture_password@localhost:5432/kapture"
            )

            if self.DATABASE_URL == default_database_url:
                raise ValueError(
                    "Production DATABASE_URL must not use "
                    "the default development database."
                )

        return self

    @model_validator(mode="after")
    def validate_environment(self):
        if (
            self.ENVIRONMENT.lower()
            not in {"development", "testing", "production"}
        ):
            raise ValueError(
                "ENVIRONMENT must be one of: "
                "development, testing, production."
            )

        return self

    @model_validator(mode="after")
    def validate_log_level(self):
        allowed_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if self.LOG_LEVEL.upper() not in allowed_levels:
            raise ValueError(
                "LOG_LEVEL must be one of: "
                "DEBUG, INFO, WARNING, ERROR, CRITICAL."
            )

        return self

    @model_validator(mode="after")
    def validate_groq_timeout(self):
        if self.GROQ_TIMEOUT_SECONDS <= 0:
            raise ValueError(
                "GROQ_TIMEOUT_SECONDS must be greater than 0."
            )

        return self


settings = Settings()



