"""Тесты для API аутентификации."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.repositories.user import UserRepository


class TestAuthRegistration:
    """Тесты регистрации пользователей."""

    async def test_register_new_user_success(self, client: AsyncClient):
        """Тест успешной регистрации нового пользователя."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_session: AsyncSession):
        """Тест регистрации с уже существующим email."""
        # Создаем первого пользователя
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user1",
                "email": "duplicate@example.com",
                "password": "Pass123!"
            }
        )

        # Пытаемся создать второго с тем же email
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "Pass123!"
            }
        )

        assert response.status_code == 400
        assert "уже зарегистрирован" in response.json()["detail"].lower() or \
               "already exists" in response.json()["detail"].lower()

    async def test_register_duplicate_username(self, client: AsyncClient):
        """Тест регистрации с уже существующим username."""
        # Создаем первого пользователя
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicateuser",
                "email": "user1@example.com",
                "password": "Pass123!"
            }
        )

        # Пытаемся создать второго с тем же username
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicateuser",
                "email": "user2@example.com",
                "password": "Pass123!"
            }
        )

        assert response.status_code == 400

    async def test_register_invalid_email(self, client: AsyncClient):
        """Тест регистрации с невалидным email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "Pass123!"
            }
        )

        assert response.status_code == 422

    async def test_register_weak_password(self, client: AsyncClient):
        """Тест регистрации со слабым паролем."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "123"
            }
        )

        assert response.status_code == 422


class TestAuthLogin:
    """Тесты входа в систему."""

    async def test_login_success(self, client: AsyncClient):
        """Тест успешного входа."""
        # Регистрируем пользователя
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "SecurePass123!"
            }
        )

        # Логинимся
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "login@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        """Тест входа с неправильным паролем."""
        # Регистрируем пользователя
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "CorrectPass123!"
            }
        )

        # Пытаемся войти с неправильным паролем
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "WrongPass123!"
            }
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Тест входа несуществующего пользователя."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "SomePass123!"
            }
        )

        assert response.status_code == 401

    async def test_login_with_username(self, client: AsyncClient):
        """Тест входа по username вместо email."""
        # Регистрируем пользователя
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "usernametest",
                "email": "username@example.com",
                "password": "Pass123!"
            }
        )

        # Логинимся по username
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "usernametest",
                "password": "Pass123!"
            }
        )

        assert response.status_code == 200
        assert "access_token" in response.json()


class TestAuthMe:
    """Тесты получения информации о текущем пользователе."""

    async def test_get_me_success(self, client: AsyncClient):
        """Тест получения информации о текущем пользователе."""
        # Регистрируемся
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "metest",
                "email": "me@example.com",
                "password": "Pass123!"
            }
        )

        # Логинимся
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "me@example.com",
                "password": "Pass123!"
            }
        )
        token = login_response.json()["access_token"]

        # Получаем информацию о себе
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "metest"
        assert data["email"] == "me@example.com"
        assert "id" in data

    async def test_get_me_without_token(self, client: AsyncClient):
        """Тест получения информации без токена."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_get_me_with_invalid_token(self, client: AsyncClient):
        """Тест получения информации с невалидным токеном."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    async def test_get_me_with_expired_token(self, client: AsyncClient):
        """Тест получения информации с истекшим токеном."""
        # Для этого теста понадобится создать токен с истекшим временем
        # Это можно сделать через фикстуру или mock
        pass  # TODO: реализовать после добавления утилит для создания токенов


class TestJWTToken:
    """Тесты работы с JWT токенами."""

    async def test_token_contains_user_info(self, client: AsyncClient):
        """Тест что токен содержит информацию о пользователе."""
        from jose import jwt
        from app.settings import settings

        # Регистрируемся и логинимся
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "tokentest",
                "email": "token@example.com",
                "password": "Pass123!"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "token@example.com",
                "password": "Pass123!"
            }
        )

        token = login_response.json()["access_token"]

        # Декодируем токен
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        assert "sub" in payload  # subject (обычно user_id или email)
        assert "exp" in payload  # expiration time

    async def test_protected_endpoint_requires_token(self, client: AsyncClient):
        """Тест что защищенные эндпоинты требуют токен."""
        response = await client.get("/api/v1/todo_items/all")

        assert response.status_code == 401
