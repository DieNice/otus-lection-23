from __future__ import annotations

import functools
import os
import sys
from abc import abstractmethod
from functools import partial
from logging import Handler
from typing import Any, Literal, TextIO, cast

from pydantic import (
    Field,
    PostgresDsn,
    PrivateAttr,
)
from pydantic_settings import BaseSettings

type ConfigNameType = Literal["prod", "dev", "test", "local_test"]


class LoggerSettings(BaseSettings):
    """Базовые настройки для Logger (loguru)"""

    enqueue: bool = Field(default=True)
    backtrace: bool = Field(default=True)
    diagnose: bool = Field(default=True)
    level: str = Field(default="INFO")
    _sink: Any = PrivateAttr(None)

    @property
    @abstractmethod
    def sink(self) -> TextIO | Handler: ...

    @property
    def as_dict(self) -> dict[str, Any]:
        return {
            "enqueue": self.enqueue,
            "backtrace": self.backtrace,
            "diagnose": self.diagnose,
            "level": self.level,
            "sink": self.sink,
        }


class LoggerProdSettings(LoggerSettings):
    @property
    def sink(self) -> TextIO | Handler:
        if self._sink is None:
            self._sink = sys.stderr
        return self._sink


class LoggerDevSettings(LoggerProdSettings):
    level: str = Field(default="DEBUG")

    @property
    def sink(self) -> TextIO | Handler:
        if self._sink is None:
            self._sink = sys.stderr
        return self._sink


class LoggerTestSettings(LoggerSettings):
    level: str = Field(default="TRACE")

    @property
    def sink(self) -> TextIO | Handler:
        if self._sink is None:
            self._sink = sys.stderr
        return self._sink


class Config(BaseSettings):
    secret_key: str = Field(alias="SECRET_KEY", default="super-secret-key")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    config_name: ConfigNameType = cast(
        ConfigNameType, os.environ.get("CONFIG_NAME", "test")
    )
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    database_uri: PostgresDsn = Field(alias="DATABASE_URI")

    def get_alembic_uri(self) -> str:
        async_conn = self.database_uri.encoded_string()
        return async_conn.replace("postgresql+asyncpg", "postgresql+psycopg2")

    @staticmethod
    def _create_config(config_name: ConfigNameType) -> LoggerSettings:
        match config_name:
            case "prod":
                return LoggerDevSettings()  # ty:ignore[missing-argument]
            case "dev":
                return LoggerDevSettings()  # ty:ignore[missing-argument]
            case "test" | "local_test":
                return LoggerTestSettings()
            case _:
                msg = "Not Allowed config name"
                raise ValueError(msg)

    logger_conf: LoggerSettings = Field(
        default_factory=partial(_create_config, config_name)
    )


@functools.lru_cache
def get_app_config() -> Config:
    """Метод-Зависимость, предоставляющий конфигурацию
    приложения.

    Returns:
        Config: Конфигурация приложения.
    """
    return Config()  # ty:ignore[missing-argument]


config = get_app_config()
