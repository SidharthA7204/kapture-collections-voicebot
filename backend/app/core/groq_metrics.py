from prometheus_client import Counter, Histogram


GROQ_REQUESTS_TOTAL = Counter(
    "groq_requests_total",
    "Total number of requests made to Groq",
)

GROQ_REQUEST_DURATION_SECONDS = Histogram(
    "groq_request_duration_seconds",
    "Duration of Groq API requests in seconds",
)

GROQ_ERRORS_TOTAL = Counter(
    "groq_errors_total",
    "Total number of Groq API errors",
)

GROQ_TIMEOUTS_TOTAL = Counter(
    "groq_timeouts_total",
    "Total number of Groq API timeout errors",
)

GROQ_SUCCESS_TOTAL = Counter(
    "groq_success_total",
    "Total number of successful Groq responses",
)
