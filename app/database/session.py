from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Получить асинхронную сессию базы данных.
    """
    async with async_session_maker() as session:
        yield session
