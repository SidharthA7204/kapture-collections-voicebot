from groq import APITimeoutError, Groq

from app.core.config import settings


class GroqServiceError(Exception):
    """Raised when the Groq service cannot generate a response."""


class GroqService:

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            timeout=settings.GROQ_TIMEOUT_SECONDS,
        )

        self.model = settings.GROQ_MODEL

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:

        messages = conversation_history or []

        messages = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in messages
        ]

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    *messages,
                ],
            )

        except APITimeoutError as exc:
            raise GroqServiceError(
                "Groq request timed out."
            ) from exc

        except Exception as exc:
            raise GroqServiceError(
                "Failed to generate response from Groq."
            ) from exc

        content = response.choices[0].message.content

        if not content:
            raise GroqServiceError(
                "Groq returned an empty response."
            )

        return content
