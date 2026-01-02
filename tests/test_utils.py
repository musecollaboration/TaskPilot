"""Вспомогательные утилиты для тестов."""

from typing import Optional

from httpx import AsyncClient


async def register_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "TestPass123!"
) -> dict:
    """
    Регистрирует нового пользователя.

    Returns:
        dict: Данные зарегистрированного пользователя
    """
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "TestPass123!"
) -> str:
    """
    Выполняет вход пользователя.

    Returns:
        str: JWT токен
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    return response.json()["access_token"]


async def create_user_and_login(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "TestPass123!"
) -> str:
    """
    Регистрирует пользователя и возвращает токен.

    Returns:
        str: JWT токен
    """
    await register_user(client, username, email, password)
    return await login_user(client, email, password)


async def create_todo_item(
    client: AsyncClient,
    token: str,
    title: str = "Test Todo",
    description: Optional[str] = None,
    category_name: str = "личное"
) -> dict:
    """
    Создает задачу.

    Returns:
        dict: Данные созданной задачи
    """
    response = await client.post(
        "/api/v1/todo_items/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "description": description,
            "category_name": category_name
        }
    )
    return response.json()


def get_auth_headers(token: str) -> dict:
    """
    Возвращает заголовки авторизации.

    Args:
        token: JWT токен

    Returns:
        dict: Заголовки с токеном
    """
    return {"Authorization": f"Bearer {token}"}
