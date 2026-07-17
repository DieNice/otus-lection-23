from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI
from loguru import logger
from prometheus_client import make_asgi_app

from .api import auth_router, health_check_router, user_router
from .config import Config, config
from .middlewares import track_latency

SUMMARY = """API для взаимодействия с Hello-world Docker"""


class AcquiringAPI(FastAPI):
    """Прокси класс FastAPI приложения, необходимый для
    типизации кастомных атрибутов экземпляра приложения.
    """


metrics_app = make_asgi_app()


def init_app(config: Config, metrics_app: Callable) -> AcquiringAPI:
    """Метод инициализации приложения FastAPI.

    Args:
        config (Config): Конфигурация приложения.

    Returns:
        FastAPI: Приложение AcquiringAPI.
    """
    logger.configure(extra={"tag": config.config_name})
    logger.add(**config.logger_conf.as_dict)

    @asynccontextmanager
    async def app_lifespan(app: AcquiringAPI) -> AsyncGenerator[None]:
        """Метод управления жизненным циклом приложения.

        Args:
            app (AcquiringAPI): Приложение Hello-world.

        Returns:
            AsyncGenerator[None]: Переча управления интерпретатору.
        """
        yield

    app = AcquiringAPI(
        title="API Hello World Docker",
        summary=SUMMARY,
        version="0.1.1",
        lifespan=app_lifespan,
    )

    app.include_router(health_check_router)
    app.include_router(user_router)
    app.include_router(auth_router)

    app.mount("/metrics", metrics_app)
    app.middleware("http")(track_latency)
    return app


app = init_app(config, metrics_app)
