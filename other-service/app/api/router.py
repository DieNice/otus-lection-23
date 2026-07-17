from fastapi import APIRouter, HTTPException, Request
from loguru import logger

example_router = APIRouter(prefix="/api/v1", tags=["auth"])


@example_router.get("/protected")
async def protected_endpoint(request: Request):
    logger.info(request.headers)
    user_id = getattr(request.headers, "x-user-id", None)
    logger.info(user_id)
    user_id = request.headers.get("x-user-id")
    logger.info(user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "message": "You are authenticated!",
        "user_id": user_id,
        "username": request.headers["x-username"],
        "email": request.headers["x-email"],
    }
