from enum import Enum


class AssistanceOutcome(str, Enum):
    NEGOTIATION_REQUIRED = "NEGOTIATION_REQUIRED"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"