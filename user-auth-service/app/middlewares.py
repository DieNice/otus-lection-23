from time import perf_counter
from http import HTTPStatus
from fastapi import Request, Response
from prometheus_client import Counter, Histogram
from loguru import logger

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Время ответа HTTP запроса",
    labelnames=["method", "endpoint", "status_code"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)

ERRORS_500 = Counter(
    "http_500_errors_total", "Total HTTP 500 errors", labelnames=["method", "endpoint"]
)

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "endpoint", "status_code"],
)


async def track_latency(request: Request, call_next):
    start = perf_counter()
    try:
        response: Response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        raise e
    finally:
        latency = start - perf_counter()

        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=str(status_code),
        ).inc()

        if status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            ERRORS_500.labels(method=request.method, endpoint=request.url.path).inc()
        logger.info(response)
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        ).observe(latency)
    return response
