from typing import Annotated

import redis.asyncio as redis_async
from fastapi import APIRouter, Depends

from app.database.dependencies import get_user_service
from app.schema.user import UserCreate
from app.service.user import UserService


router = APIRouter(
    prefix='/user',
    tags=['user'],
)

redis = redis_async.from_url("redis://localhost:6379")


@router.post(
    "/register",
    status_code=201
)
async def register(
    user_schema: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    """
    Эндпоинт для регистрации нового пользователя.
    """
    user, token = await user_service.register_user(
        user_schema=user_schema
    )
    await redis.set(
        f"email_confirm:{token}",  # ключ
        str(user.id),              # значение
        ex=43200                   # TTL в секундах (12 часов)
    )
    return {
        'message': 'Пользователь добавлен! Подтвердите вашу электронную почту для активации аккаунта.'
    }
