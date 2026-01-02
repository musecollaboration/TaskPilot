from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_service import AuthService
from app.auth.client.google import GoogleAuthClient
from app.auth.client.vk import VKAuthClient
from app.auth.client.yandex import YandexAuthClient
from app.database.session import get_db
from app.repositories.todo_item import TodoItemRepository
from app.repositories.user import UserRepository
from app.service.todo_item import TodoItemService
from app.service.user import UserService
from app.settings import Settings


async def get_user_repository(
        db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    """Получить репозиторий для работы с пользователями."""
    return UserRepository(db)


async def get_todo_db(
        db: Annotated[AsyncSession, Depends(get_db)]
) -> TodoItemRepository:
    """Получить репозиторий для работы с элементами списка дел."""
    return TodoItemRepository(db)


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AuthService:
    """Получить сервис для работы с аутентификацией."""
    return AuthService(
        user_repository=UserRepository(db),
        google_client=GoogleAuthClient(settings=Settings()),
        yandex_client=YandexAuthClient(settings=Settings()),
        vk_client =VKAuthClient(settings=Settings())
    )


async def get_todo_item_service(
        repository: Annotated[TodoItemRepository, Depends(get_todo_db)]
) -> TodoItemService:
    """Получить сервис для работы с элементами списка дел."""
    return TodoItemService(repository=repository)


async def get_user_service(
        user_repository: Annotated[UserRepository, Depends(get_user_repository)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserService:
    """Получить сервис для работы с пользователями."""
    return UserService(
        user_repository=user_repository,
        auth_service=auth_service
    )



