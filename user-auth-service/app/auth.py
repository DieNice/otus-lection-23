import datetime as dt
from datetime import datetime, timedelta
from typing import TypedDict

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenVerifyType(TypedDict):
    username: str
    user_id: int


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=dt.timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=dt.timezone.utc) + timedelta(
            minutes=config.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
    return encoded_jwt


def verify_token(token: str) -> TokenVerifyType | None:
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            return None
        return {"username": username, "user_id": user_id}
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
