import datetime as dt
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy.types import Boolean, DateTime, String

from app.utils import pwd_context


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: MappedColumn[int] = mapped_column(primary_key=True)
    username: MappedColumn[str] = mapped_column(String(256))
    first_name: MappedColumn[str] = mapped_column(String())
    last_name: MappedColumn[str] = mapped_column(String())
    email: MappedColumn[str] = mapped_column(String(), unique=True)
    phone: MappedColumn[str] = mapped_column(String(), unique=True)
    hashed_password: MappedColumn[str] = mapped_column(String(), nullable=False)
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=dt.timezone.utc)
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=dt.timezone.utc)
    )
    is_active: MappedColumn[bool] = mapped_column(Boolean(), default=True)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
