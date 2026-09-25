from prometheus_client import Counter


HEALTH_CHECKS_TOTAL = Counter(
    "health_checks_total",
    "Total number of health checks performed",
)

HEALTH_CHECK_FAILURES_TOTAL = Counter(
    "health_check_failures_total",
    "Total number of failed health checks",
)

READINESS_CHECKS_TOTAL = Counter(
    "readiness_checks_total",
    "Total number of readiness checks performed",
)

READINESS_CHECK_FAILURES_TOTAL = Counter(
    "readiness_check_failures_total",
    "Total number of failed readiness checks",
)
