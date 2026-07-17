from pydantic import BaseModel, EmailStr, Field


class UserQuery(BaseModel):
    user_id: int = Field(alias="UserId", ge=1, examples=123)


class UserBody(BaseModel):
    """Входная модель пользователей"""

    username: str = Field(min_length=3, max_length=50)
    first_name: str = Field(serialization_alias="firstName", max_length=50)
    last_name: str = Field(serialization_alias="lastName", max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    phone: str = Field(max_length=20)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    """Входная модель пользователей"""

    id: int
    username: str
    first_name: str = Field(serialization_alias="firstName", max_length=50)
    last_name: str = Field(serialization_alias="lastName", max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    is_active: bool


class UpdateUser(BaseModel):
    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
    email: EmailStr
    phone: str = Field(max_length=20)
    password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None
