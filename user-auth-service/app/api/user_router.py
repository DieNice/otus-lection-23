from typing import Annotated

from fastapi import Depends, HTTPException, Path, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_password_hash

from ..models import User
from .deps import get_current_active_user, get_session
from .schemas import UpdateUser, UserBody, UserResponse

user_router = APIRouter(tags=["user"])


@user_router.get(
    "/user/profile",
    summary="Get current user profile",
    description="Get profile of currently authenticated user",
)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone=current_user.phone,
        is_active=current_user.is_active,
    )


@user_router.put(
    "/user/profile",
    summary="Update current user profile",
    description="Update profile of currently authenticated user",
)
async def update_my_profile(
    body: UpdateUser,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    try:
        # Update only provided fields
        if body.first_name is not None:
            current_user.first_name = body.first_name
        if body.last_name is not None:
            current_user.last_name = body.last_name
        if body.email is not None:
            # Check if email is taken by another user
            existing = await session.execute(
                select(User).where(User.email == body.email, User.id != current_user.id)
            )
            if existing.scalar_one_or_none():
                return JSONResponse(
                    {"message": "Email already in use"}, status_code=400
                )
            current_user.email = body.email
        if body.phone is not None:
            current_user.phone = body.phone
        if body.password is not None:
            current_user.hashed_password = get_password_hash(body.password)

        await session.commit()
    except SQLAlchemyError as error:
        logger.error(error)
        return JSONResponse(
            content={"code": 0, "message": "Can't update user"}, status_code=500
        )

    return JSONResponse({"message": "Profile updated successfully"})


@user_router.post(
    "/user/",
    summary="Create user",
    description="This can only be done by the logged in user.",
)
async def create_user(
    body: UserBody, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    try:
        # Check if user exists
        existing_user = await session.execute(
            select(User).where(
                (User.username == body.username) | (User.email == body.email)
            )
        )
        if existing_user.scalar_one_or_none():
            return JSONResponse(
                {"message": "Username or email already exists"}, status_code=400
            )

        # Create user with temporary password (should be changed)
        temp_password = "temp_password_123"  # In production, should send email
        session.add(
            User(
                username=body.username,
                first_name=body.first_name,
                last_name=body.last_name,
                email=body.email,
                phone=body.phone,
                hashed_password=get_password_hash(temp_password),
            )
        )
        await session.commit()
    except SQLAlchemyError as error:
        logger.error(error)
        return JSONResponse({"message": "Failed operation"}, status_code=500)
    return JSONResponse({"message": "Successful operation"})


@user_router.get(
    "/user/{userId}",
    summary="Get user by id",
)
async def get_user_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_id: int = Path(description="ID of user", ge=1, example=123, alias="userId"),
) -> UserResponse:
    """
    Returns a user based on a single ID.

    Если пользователь не имеет доступа к запрашиваемым данным, возвращается ошибка.

    - **userId**: Уникальный идентификатор пользователя
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile",
        )

    try:
        query = select(User).filter_by(id=user_id)
        result = await session.execute(query)
        user_info = result.scalar_one_or_none()

        if user_info:
            return UserResponse(
                id=user_info.id,
                username=user_info.username,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
                email=user_info.email,
                phone=user_info.phone,
                is_active=user_info.is_active,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
    except SQLAlchemyError as error:
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )


@user_router.delete(
    "/user/{userId}",
    summary="Delete user by id",
)
async def delete_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_id: int = Path(description="ID of user", ge=1, example=123, alias="userId"),
) -> Response:
    # Check authorization
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    try:
        query = select(User).filter_by(id=user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
    except SQLAlchemyError as error:
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Can't delete user",
        )

    return Response(status_code=204)


@user_router.put(
    "/user/{userId}",
    summary="Update user by id",
)
async def update_user(
    body: UpdateUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_id: int = Path(description="ID of user", ge=1, example=123, alias="userId"),
) -> JSONResponse:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own account",
        )

    try:
        query = select(User).filter_by(id=user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            if body.first_name is not None:
                user.first_name = body.first_name
            if body.last_name is not None:
                user.last_name = body.last_name
            if body.email is not None:
                # Check if email is taken by another user
                existing = await session.execute(
                    select(User).where(User.email == body.email, User.id != user_id)
                )
                if existing.scalar_one_or_none():
                    return JSONResponse(
                        {"message": "Email already in use"}, status_code=400
                    )
                user.email = body.email
            if body.phone is not None:
                user.phone = body.phone
            if body.password is not None:
                user.hashed_password = get_password_hash(body.password)
            await session.commit()
        else:
            return JSONResponse({"message": "User not found"}, status_code=404)
    except SQLAlchemyError as error:
        logger.error(error)
        return JSONResponse(
            content={"code": 0, "message": "Can't update user"}, status_code=500
        )

    return JSONResponse({"message": "User updated successfully"})
