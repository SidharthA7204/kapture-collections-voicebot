from prometheus_client import Counter, Gauge, Histogram


VOICE_CALLS_STARTED_TOTAL = Counter(
    "voice_calls_started_total",
    "Total number of voice calls started",
)

VOICE_CALLS_COMPLETED_TOTAL = Counter(
    "voice_calls_completed_total",
    "Total number of voice calls completed",
)

VOICE_CALLS_ACTIVE = Gauge(
    "voice_calls_active",
    "Current number of active voice calls",
)

VOICE_CALL_DURATION_SECONDS = Histogram(
    "voice_call_duration_seconds",
    "Duration of completed voice calls in seconds",
)

VOICE_CALLS_ENDED_TOTAL = Counter(
    "voice_calls_ended_total",
    "Total number of voice call end events recorded",
)
