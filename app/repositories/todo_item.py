from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models.enums import CategoryName
from app.database.models.todo_category import TodoCategory
from app.database.models.todo_item import TodoItem


@dataclass
class TodoItemRepository:
    db: AsyncSession

    async def check_category_exists(self, category_name: CategoryName) -> TodoCategory | None:
        """
        Проверить, существует ли категория с данным названием.
        """
        return await self.db.scalar(
            select(TodoCategory)
            .where(TodoCategory.name == category_name)
        )

    async def get_todo_items(self, user_id: UUID) -> Sequence[TodoItem]:
        """
        Получить все элементы списка дел.
        """
        todo_items = await self.db.scalars(select(TodoItem)
                                           .where(TodoItem.user_id == user_id)
                                           .order_by(TodoItem.created_at.desc())
                                           )
        return todo_items.all()

    async def create_todo_item(self, data: dict) -> TodoItem:
        """
        Создать новый элемент списка дел.
        """
        item = TodoItem(**data)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_todo_item(self, todo_item_id: UUID, user_id: UUID) -> TodoItem:
        """
        Получить элемент списка дел по идентификатору.
        """
        todo_item = await self.db.scalar(
            select(TodoItem)
            .where(TodoItem.id == todo_item_id)
            .where(TodoItem.user_id == user_id)
        )
        return todo_item
    
    async def get_todo_item_by_title(self, title: str, user_id: UUID) -> TodoItem | None:
        """
        Получить элемент списка дел по названию.
        """
        return await self.db.scalar(
            select(TodoItem)
            .where(TodoItem.title == title)
            .where(TodoItem.user_id == user_id)
        )

    async def update_todo_item(self, todo_item: TodoItem, data: dict) -> TodoItem:
        """
        Обновить элемент списка дел.
        """
        for key, value in data.items():
            setattr(todo_item, key, value)
        await self.db.commit()
        await self.db.refresh(todo_item)
        return todo_item

    async def delete_todo_item(self, todo_item: TodoItem) -> dict[str, str]:
        """
        Удалить элемент списка дел.
        """
        await self.db.delete(todo_item)
        await self.db.commit()
        return {"detail": "Элемент списка дел успешно удален"}
