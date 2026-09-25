from prometheus_client import Counter


APPLICATION_ERRORS_TOTAL = Counter(
    "application_errors_total",
    "Total number of application errors",
    ["error_type"],
)

DATABASE_ERRORS_TOTAL = Counter(
    "application_database_errors_total",
    "Total number of database errors",
)

AI_SERVICE_ERRORS_TOTAL = Counter(
    "application_ai_service_errors_total",
    "Total number of AI service errors",
)

UNEXPECTED_ERRORS_TOTAL = Counter(
    "application_unexpected_errors_total",
    "Total number of unexpected application errors",
)

VALIDATION_ERRORS_TOTAL = Counter(
    "application_validation_errors_total",
    "Total number of request validation errors",
)
