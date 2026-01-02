"""Тесты для API пользователей."""

import pytest
from httpx import AsyncClient


async def create_user_and_login(client: AsyncClient, username: str = "testuser", email: str = "test@example.com", is_admin: bool = False) -> str:
    """Вспомогательная функция для создания пользователя и получения токена."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "TestPass123!"
        }
    )

    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "TestPass123!"
        }
    )

    return response.json()["access_token"]


class TestUserEndpoints:
    """Тесты эндпоинтов пользователей."""

    async def test_get_all_users(self, client: AsyncClient):
        """Тест получения всех пользователей."""
        # Создаем несколько пользователей
        await create_user_and_login(client, "user1", "user1@example.com")
        await create_user_and_login(client, "user2", "user2@example.com")
        token = await create_user_and_login(client, "user3", "user3@example.com")

        response = await client.get(
            "/api/v1/users/all",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert all("username" in user for user in data)
        assert all("email" in user for user in data)
        assert all("password" not in user for user in data)
        assert all("hashed_password" not in user for user in data)

    async def test_get_all_users_without_auth(self, client: AsyncClient):
        """Тест получения пользователей без авторизации."""
        response = await client.get("/api/v1/users/all")

        assert response.status_code == 401

    async def test_get_user_by_id(self, client: AsyncClient):
        """Тест получения пользователя по ID."""
        token = await create_user_and_login(client, "testuser", "test@example.com")

        # Получаем информацию о себе чтобы узнать ID
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        user_id = me_response.json()["id"]

        # Получаем пользователя по ID
        response = await client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"
        assert "password" not in data

    async def test_get_user_not_found(self, client: AsyncClient):
        """Тест получения несуществующего пользователя."""
        token = await create_user_and_login(client)
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await client.get(
            f"/api/v1/users/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestUserProfile:
    """Тесты профиля пользователя."""

    async def test_user_has_correct_fields(self, client: AsyncClient):
        """Тест что пользователь содержит правильные поля."""
        token = await create_user_and_login(client, "profileuser", "profile@example.com")

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Обязательные поля
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "is_admin" in data
        assert "is_active" in data
        assert "created_at" in data

        # Поля которых не должно быть
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_new_user_is_not_admin(self, client: AsyncClient):
        """Тест что новый пользователь не является админом."""
        token = await create_user_and_login(client)

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["is_admin"] is False

    async def test_new_user_is_active(self, client: AsyncClient):
        """Тест что новый пользователь активен."""
        token = await create_user_and_login(client)

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True


class TestUserSecurity:
    """Тесты безопасности пользователей."""

    async def test_password_not_exposed_in_response(self, client: AsyncClient):
        """Тест что пароль не возвращается в ответах API."""
        token = await create_user_and_login(client)

        # Проверяем /auth/me
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        me_data = me_response.json()
        assert "password" not in me_data
        assert "hashed_password" not in me_data

        # Проверяем /users/all
        users_response = await client.get(
            "/api/v1/users/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        users_data = users_response.json()
        for user in users_data:
            assert "password" not in user
            assert "hashed_password" not in user

    async def test_user_isolation(self, client: AsyncClient):
        """Тест что пользователи изолированы друг от друга."""
        # Создаем двух пользователей с задачами
        token1 = await create_user_and_login(client, "user1", "user1@example.com")
        await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token1}"},
            json={"title": "Задача пользователя 1"}
        )

        token2 = await create_user_and_login(client, "user2", "user2@example.com")
        await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token2}"},
            json={"title": "Задача пользователя 2"}
        )

        # Проверяем что каждый видит только свои задачи
        response1 = await client.get(
            "/api/v1/todo_items/all",
            headers={"Authorization": f"Bearer {token1}"}
        )
        todos1 = response1.json()
        assert len(todos1) == 1
        assert todos1[0]["title"] == "Задача пользователя 1"

        response2 = await client.get(
            "/api/v1/todo_items/all",
            headers={"Authorization": f"Bearer {token2}"}
        )
        todos2 = response2.json()
        assert len(todos2) == 1
        assert todos2[0]["title"] == "Задача пользователя 2"
