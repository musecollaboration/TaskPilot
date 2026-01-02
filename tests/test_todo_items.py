"""Тесты для API управления задачами (Todo Items)."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


async def create_user_and_login(client: AsyncClient, username: str = "testuser", email: str = "test@example.com") -> str:
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


class TestTodoItemCreate:
    """Тесты создания задач."""

    async def test_create_todo_item_success(self, client: AsyncClient):
        """Тест успешного создания задачи."""
        token = await create_user_and_login(client)

        response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Купить молоко",
                "description": "Купить 2 литра молока",
                "category_name": "покупки"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Купить молоко"
        assert data["description"] == "Купить 2 литра молока"
        assert data["category_name"] == "покупки"
        assert data["completed"] is False
        assert "id" in data
        assert "user_id" in data

    async def test_create_todo_item_with_date(self, client: AsyncClient):
        """Тест создания задачи с датой выполнения."""
        token = await create_user_and_login(client)
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Встреча",
                "description": "Встреча с клиентом",
                "category_name": "работа",
                "date_of_execution": tomorrow
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["date_of_execution"] == tomorrow

    async def test_create_todo_item_minimal(self, client: AsyncClient):
        """Тест создания задачи с минимальными данными."""
        token = await create_user_and_login(client)

        response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Простая задача"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Простая задача"
        assert data["description"] is None
        assert data["category_name"] == "личное"  # Значение по умолчанию

    async def test_create_todo_item_without_auth(self, client: AsyncClient):
        """Тест создания задачи без авторизации."""
        response = await client.post(
            "/api/v1/todo_items/",
            json={
                "title": "Задача без авторизации"
            }
        )

        assert response.status_code == 401

    async def test_create_todo_item_invalid_category(self, client: AsyncClient):
        """Тест создания задачи с невалидной категорией."""
        token = await create_user_and_login(client)

        response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Задача",
                "category_name": "несуществующая_категория"
            }
        )

        assert response.status_code == 422


class TestTodoItemRead:
    """Тесты чтения задач."""

    async def test_get_all_todo_items(self, client: AsyncClient):
        """Тест получения всех задач пользователя."""
        token = await create_user_and_login(client)

        # Создаем несколько задач
        for i in range(3):
            await client.post(
                "/api/v1/todo_items/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": f"Задача {i + 1}",
                    "description": f"Описание задачи {i + 1}"
                }
            )

        # Получаем все задачи
        response = await client.get(
            "/api/v1/todo_items/all",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(item["title"].startswith("Задача") for item in data)

    async def test_get_all_todo_items_empty(self, client: AsyncClient):
        """Тест получения задач когда их нет."""
        token = await create_user_and_login(client)

        response = await client.get(
            "/api/v1/todo_items/all",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_todo_item_by_id(self, client: AsyncClient):
        """Тест получения задачи по ID."""
        token = await create_user_and_login(client)

        # Создаем задачу
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Тестовая задача",
                "description": "Описание"
            }
        )
        todo_id = create_response.json()["id"]

        # Получаем задачу по ID
        response = await client.get(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == "Тестовая задача"

    async def test_get_todo_item_not_found(self, client: AsyncClient):
        """Тест получения несуществующей задачи."""
        token = await create_user_and_login(client)
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await client.get(
            f"/api/v1/todo_items/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    async def test_get_other_user_todo_item(self, client: AsyncClient):
        """Тест что пользователь не может получить чужую задачу."""
        # Создаем первого пользователя и его задачу
        token1 = await create_user_and_login(client, "user1", "user1@example.com")
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token1}"},
            json={"title": "Задача пользователя 1"}
        )
        todo_id = create_response.json()["id"]

        # Создаем второго пользователя
        token2 = await create_user_and_login(client, "user2", "user2@example.com")

        # Пытаемся получить задачу первого пользователя
        response = await client.get(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 404


class TestTodoItemUpdate:
    """Тесты обновления задач."""

    async def test_update_todo_item_title(self, client: AsyncClient):
        """Тест обновления заголовка задачи."""
        token = await create_user_and_login(client)

        # Создаем задачу
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Старый заголовок"}
        )
        todo_id = create_response.json()["id"]

        # Обновляем заголовок
        response = await client.patch(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Новый заголовок"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Новый заголовок"

    async def test_update_todo_item_completed(self, client: AsyncClient):
        """Тест отметки задачи как выполненной."""
        token = await create_user_and_login(client)

        # Создаем задачу
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Задача для выполнения"}
        )
        todo_id = create_response.json()["id"]

        # Отмечаем как выполненную
        response = await client.patch(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"completed": True}
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True

    async def test_update_todo_item_multiple_fields(self, client: AsyncClient):
        """Тест обновления нескольких полей одновременно."""
        token = await create_user_and_login(client)

        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Задача"}
        )
        todo_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Обновленная задача",
                "description": "Новое описание",
                "completed": True,
                "category_name": "работа"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Обновленная задача"
        assert data["description"] == "Новое описание"
        assert data["completed"] is True
        assert data["category_name"] == "работа"

    async def test_update_other_user_todo_item(self, client: AsyncClient):
        """Тест что пользователь не может обновить чужую задачу."""
        token1 = await create_user_and_login(client, "user1", "user1@example.com")
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token1}"},
            json={"title": "Задача пользователя 1"}
        )
        todo_id = create_response.json()["id"]

        token2 = await create_user_and_login(client, "user2", "user2@example.com")

        response = await client.patch(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token2}"},
            json={"title": "Попытка изменить"}
        )

        assert response.status_code == 404


class TestTodoItemDelete:
    """Тесты удаления задач."""

    async def test_delete_todo_item_success(self, client: AsyncClient):
        """Тест успешного удаления задачи."""
        token = await create_user_and_login(client)

        # Создаем задачу
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Задача для удаления"}
        )
        todo_id = create_response.json()["id"]

        # Удаляем задачу
        response = await client.delete(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # Проверяем что задача действительно удалена
        get_response = await client.get(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404

    async def test_delete_nonexistent_todo_item(self, client: AsyncClient):
        """Тест удаления несуществующей задачи."""
        token = await create_user_and_login(client)
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await client.delete(
            f"/api/v1/todo_items/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    async def test_delete_other_user_todo_item(self, client: AsyncClient):
        """Тест что пользователь не может удалить чужую задачу."""
        token1 = await create_user_and_login(client, "user1", "user1@example.com")
        create_response = await client.post(
            "/api/v1/todo_items/",
            headers={"Authorization": f"Bearer {token1}"},
            json={"title": "Задача пользователя 1"}
        )
        todo_id = create_response.json()["id"]

        token2 = await create_user_and_login(client, "user2", "user2@example.com")

        response = await client.delete(
            f"/api/v1/todo_items/{todo_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 404
