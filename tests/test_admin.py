"""Тесты для административных эндпоинтов."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.repositories.user import UserRepository


async def create_user_and_login(client: AsyncClient, username: str, email: str) -> str:
    """Создает пользователя и возвращает токен."""
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


async def make_user_admin(test_session: AsyncSession, email: str):
    """Делает пользователя администратором."""
    user_repo = UserRepository(test_session)
    user = await user_repo.get_user_by_email(email)
    if user:
        user.is_admin = True
        await test_session.commit()


class TestAdminAccess:
    """Тесты доступа к административным эндпоинтам."""

    async def test_admin_can_access_admin_endpoints(self, client: AsyncClient, test_session: AsyncSession):
        """Тест что админ имеет доступ к админским эндпоинтам."""
        # Создаем пользователя и делаем его админом
        admin_token = await create_user_and_login(client, "admin", "admin@example.com")
        await make_user_admin(test_session, "admin@example.com")

        # Пытаемся получить все задачи всех пользователей
        response = await client.get(
            "/api/v1/admin/todo_items/all",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200

    async def test_regular_user_cannot_access_admin_endpoints(self, client: AsyncClient):
        """Тест что обычный пользователь не имеет доступа к админским эндпоинтам."""
        # Создаем обычного пользователя
        user_token = await create_user_and_login(client, "regular", "regular@example.com")

        # Пытаемся получить доступ к админскому эндпоинту
        response = await client.get(
            "/api/v1/admin/todo_items/all",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403

    async def test_admin_endpoints_without_auth(self, client: AsyncClient):
        """Тест доступа к админским эндпоинтам без авторизации."""
        response = await client.get("/api/v1/admin/todo_items/all")

        assert response.status_code == 401


class TestAdminTodoOperations:
    """Тесты административных операций с задачами."""

    async def test_admin_can_see_all_users_todos(self, client: AsyncClient, test_session: AsyncSession):
        """Тест что админ видит задачи всех пользователей."""
        # Создаем обычных пользователей с задачами
        user1_token = await create_user_and_login(client, "user1", "user1@example.com")
        await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"title": "Задача пользователя 1"}
        )

        user2_token = await create_user_and_login(client, "user2", "user2@example.com")
        await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {user2_token}"},
            json={"title": "Задача пользователя 2"}
        )

        # Создаем админа
        admin_token = await create_user_and_login(client, "admin", "admin@example.com")
        await make_user_admin(test_session, "admin@example.com")

        # Админ получает все задачи
        response = await client.get(
            "/api/v1/admin/todo_items/all",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        todos = response.json()
        assert len(todos) >= 2

        # Проверяем что есть задачи обоих пользователей
        titles = [todo["title"] for todo in todos]
        assert "Задача пользователя 1" in titles
        assert "Задача пользователя 2" in titles

    async def test_admin_can_delete_any_todo(self, client: AsyncClient, test_session: AsyncSession):
        """Тест что админ может удалить любую задачу."""
        # Создаем пользователя с задачей
        user_token = await create_user_and_login(client, "user", "user@example.com")
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Задача для удаления админом"}
        )
        todo_id = create_response.json()["id"]

        # Создаем админа
        admin_token = await create_user_and_login(client, "admin", "admin@example.com")
        await make_user_admin(test_session, "admin@example.com")

        # Админ удаляет задачу пользователя
        response = await client.delete(
            f"/api/v1/admin/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204

        # Проверяем что задача действительно удалена
        get_response = await client.get(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert get_response.status_code == 404

    async def test_regular_user_cannot_delete_admin_todo(self, client: AsyncClient, test_session: AsyncSession):
        """Тест что обычный пользователь не может удалить задачу через админский эндпоинт."""
        # Создаем админа с задачей
        admin_token = await create_user_and_login(client, "admin", "admin@example.com")
        await make_user_admin(test_session, "admin@example.com")
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "Задача админа"}
        )
        todo_id = create_response.json()["id"]

        # Создаем обычного пользователя
        user_token = await create_user_and_login(client, "user", "user@example.com")

        # Пользователь пытается удалить через админский эндпоинт
        response = await client.delete(
            f"/api/v1/admin/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403

    async def test_admin_get_empty_todos_list(self, client: AsyncClient, test_session: AsyncSession):
        """Тест что админ получает пустой список если нет задач."""
        admin_token = await create_user_and_login(client, "admin", "admin@example.com")
        await make_user_admin(test_session, "admin@example.com")

        response = await client.get(
            "/api/v1/admin/todo_items/all",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json() == []


class TestAdminSecurity:
    """Тесты безопасности административной панели."""

    async def test_admin_status_not_exposed_in_registration(self, client: AsyncClient):
        """Тест что нельзя зарегистрироваться как админ."""
        # Пытаемся зарегистрироваться с is_admin=True
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "hacker",
                "email": "hacker@example.com",
                "password": "Pass123!",
                "is_admin": True  # Попытка стать админом
            }
        )

        # Регистрация должна пройти, но пользователь не должен быть админом
        if response.status_code == 201:
            login_response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "hacker@example.com",
                    "password": "Pass123!"
                }
            )
            token = login_response.json()["access_token"]

            me_response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert me_response.json()["is_admin"] is False

    async def test_admin_cannot_access_with_regular_token(self, client: AsyncClient):
        """Тест что нельзя получить админский доступ с обычным токеном."""
        user_token = await create_user_and_login(client, "user", "user@example.com")

        response = await client.get(
            "/api/v1/admin/todo_items/all",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower() or \
               "forbidden" in response.json()["detail"].lower()
