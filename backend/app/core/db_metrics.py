from prometheus_client import Counter, Gauge


DB_CONNECTIONS_CHECKED_OUT_TOTAL = Counter(
    "db_connections_checked_out_total",
    "Total number of database connections checked out from the pool",
)

DB_CONNECTIONS_CHECKED_IN_TOTAL = Counter(
    "db_connections_checked_in_total",
    "Total number of database connections returned to the pool",
)

DB_CONNECTION_ERRORS_TOTAL = Counter(
    "db_connection_errors_total",
    "Total number of database connection errors",
)

DB_CONNECTIONS_IN_USE = Gauge(
    "db_connections_in_use",
    "Current number of database connections checked out from the pool",
)

DB_CONNECTION_POOL_SIZE = Gauge(
    "db_connection_pool_size",
    "Configured database connection pool size",
)
