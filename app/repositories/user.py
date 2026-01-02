from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models.user import User


@dataclass
class UserRepository:
    db: AsyncSession

    async def get_user_by_id(self, user_id: UUID):
        """
        Получить пользователя по его идентификатору.
        """
        return await self.db.scalar(
            select(User).
            where(User.id == user_id)
        )

    async def get_by_username(self, username: str):
        """
        Получить активного пользователя по имени пользователя.
        """
        return await self.db.scalar(
            select(User)
            .where(User.username == username)
            .where(User.is_active == True)
        )

    async def create_user(self, user_data: dict):
        """
        Создать нового пользователя.
        """
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_email(self, email: str):
        """
        Получить пользователя по его электронному адресу.
        """
        return await self.db.scalar(
            select(User)
            .where(User.email == email)
            .where(User.is_active == True)
        )

    async def update_user(self, user: int, user_data: dict):
        """
        Обновить данные пользователя.
        """
        for key, value in user_data.items():
            setattr(user, key, value)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int):
        """
        Удалить пользователя по его идентификатору.
        """
        pass
