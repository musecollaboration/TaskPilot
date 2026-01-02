from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database.models.todo_category import TodoCategory
from app.repositories.todo_item import TodoItemRepository
from app.schema.todo_item import TodoItemCreate, TodoItemUpdate


@dataclass
class TodoItemService:
    repository: TodoItemRepository

    async def get_todo_items(self, user_id: UUID):
        """
        Получить все элементы списка дел.

        - Возвращает список всех задач из базы данных.
        - В случае ошибки базы данных выбрасывает HTTPException с кодом 500.
        """
        try:
            return await self.repository.get_todo_items(
                user_id=user_id
            )
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")

    async def create_todo_item(self, schema: TodoItemCreate, user_id: UUID):
        """
        Создать новый элемент списка дел.

        - Получает данные задачи из схемы.
        - Проверяет наличие имени категории, если не указано — выбрасывает ошибку 400.
        - Находит категорию по имени, если не найдена — выбрасывает ошибку 400.
        - Добавляет задачу в базу данных с найденным category_id.
        - В случае нарушения уникальности названия задачи выбрасывает ошибку 400.
        - В случае других ошибок базы данных выбрасывает ошибку 500.
        """
        try:
            data = schema.model_dump()
            category_name = data.pop('category_name', None)
            if not category_name:
                raise HTTPException(status_code=400, detail="Не указано имя категории")

            category: TodoCategory = await self.repository.check_category_exists(
                category_name=category_name
            )
            if not category:
                raise HTTPException(status_code=400, detail="Нет ID категории")
            data['category_id'] = category.id
            data['user_id'] = user_id
            
            # Проверка на уникальность названия задачи
            new_item_title = data.get('title', None)
            old_item_title = await self.repository.get_todo_item_by_title(
                title=new_item_title,
                user_id=user_id
            )

            if old_item_title:
                raise HTTPException(status_code=400, detail="Задача с таким названием уже существует")
            return await self.repository.create_todo_item(
                data=data
            )
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")

    async def get_todo_item(self, todo_item_id: UUID, user_id: UUID):
        """
        Получить элемент списка дел по ID.

        - Ищет задачу по уникальному идентификатору.
        - Если задача не найдена, выбрасывает ошибку 404.
        - В случае ошибки базы данных выбрасывает ошибку 500.
        """
        try:
            todo_item = await self.repository.get_todo_item(
                todo_item_id=todo_item_id,
                user_id=user_id
            )
            if not todo_item:
                raise HTTPException(status_code=404, detail="Элемент списка дел не найден")
            return todo_item
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")

    async def update_todo_item(self, todo_item_id: UUID, schema: TodoItemUpdate, user_id: UUID):
        """
        Обновить элемент списка дел.

        - Получает данные для обновления из схемы.
        - Находит задачу по уникальному идентификатору.
        - Если передано новое имя категории, ищет категорию по имени и обновляет category_id.
        - Обновляет указанные поля задачи.
        - Возвращает обновлённую задачу.
        - В случае ошибки базы данных выбрасывает HTTPException с кодом 500.
        """
        try:
            data = schema.model_dump(exclude_unset=True)
            todo_item = await self.get_todo_item(
                todo_item_id=todo_item_id,
                user_id=user_id
            )
            category_name = data.pop('category_name', None)
            if not category_name:
                raise HTTPException(status_code=400, detail="Не указано имя категории")
            category: TodoCategory = await self.repository.check_category_exists(category_name)
            if category_name and not category:
                raise HTTPException(status_code=400, detail="Нет такой категории")
            data['category_id'] = category.id
            data['user_id'] = user_id
            todo_item = await self.repository.update_todo_item(
                todo_item=todo_item,
                data=data
            )
            return todo_item
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")

    async def delete_todo_item(self, todo_item_id: UUID, user_id: UUID):
        """
        Удалить элемент списка дел.

        - Находит задачу по уникальному идентификатору.
        - Если задача не найдена, выбрасывает ошибку 404.
        - Удаляет найденную задачу из базы данных.
        - Возвращает сообщение об успешном удалении.
        - В случае ошибки базы данных выбрасывает HTTPException с кодом 500.
        """
        try:
            todo_item = await self.get_todo_item(
                todo_item_id=todo_item_id,
                user_id=user_id
            )
            await self.repository.delete_todo_item(todo_item)
            return {"message": "Элемент списка дел успешно удален"}
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
