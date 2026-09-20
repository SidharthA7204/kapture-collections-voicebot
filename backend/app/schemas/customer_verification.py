from datetime import date

from pydantic import BaseModel, Field, field_validator


class CustomerVerificationRequest(BaseModel):
    phone: str = Field(
        min_length=10,
        max_length=10,
        pattern=r"^\d{10}$",
    )
    dob: date

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        if value > date.today():
            raise ValueError(
                "Date of birth cannot be in the future"
            )

        if value < date(1900, 1, 1):
            raise ValueError(
                "Date of birth is outside the supported range"
            )

        return value


class CustomerVerificationResponse(BaseModel):
    call_id: str
    authenticated: bool
    current_state: str
