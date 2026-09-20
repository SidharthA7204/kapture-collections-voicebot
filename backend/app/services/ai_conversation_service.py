from app.ai.prompts.collections import (
    COLLECTIONS_SYSTEM_PROMPT,
)
from app.services.groq_service import GroqService


class AIConversationService:

    def __init__(
        self,
        groq_service: GroqService,
    ):
        self.groq_service = groq_service

    def generate_response(
        self,
        user_message: str,
        current_state: str | None = None,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:

        if not user_message.strip():
            raise ValueError(
                "User message cannot be empty."
            )

        system_prompt = COLLECTIONS_SYSTEM_PROMPT

        if current_state:
            system_prompt += (
                "\n\nCurrent call state:\n"
                f"{current_state}\n"
                "\nFollow the rules appropriate "
                "for this call state."
            )

        return self.groq_service.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=conversation_history,
        )
