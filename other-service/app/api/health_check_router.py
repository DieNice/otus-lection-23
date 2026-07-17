from typing import Literal, TypedDict

from fastapi.routing import APIRouter
from loguru import logger

health_check_router = APIRouter(tags=["Статус приложения"])


class HealthResponse(TypedDict):
    status: Literal["OK"]


@health_check_router.get("/api/v1/health/", summary="Проверка состояния сервиса")
async def health_check_route() -> HealthResponse:
    """Эндпоинт для проверки состояния сервиса"""

    logger.info("Healthcheck endpoint: service is healthy")
    return {"status": "OK"}
