import datetime as dt
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy.types import Boolean, DateTime, String


class Base(DeclarativeBase):
    pass


class Example(Base):
    __tablename__ = "example"

    id: MappedColumn[int] = mapped_column(primary_key=True)
