from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api import example_router, health_check_router
from .config import Config, config

SUMMARY = """API для взаимодействия с Hello-world Docker"""


class AcquiringAPI(FastAPI):
    """Прокси класс FastAPI приложения, необходимый для
    типизации кастомных атрибутов экземпляра приложения.
    """


def init_app(config: Config) -> AcquiringAPI:
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
    app.include_router(example_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = init_app(config)
