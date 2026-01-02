"""
Конфигурация pytest для тестов TaskPilot.
Содержит фикстуры для настройки тестовой среды.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.database import Base
from app.database.dependencies import get_session
from app.main import app
from app.settings import Settings


# Настройки для тестовой БД
TEST_DATABASE_URL = "postgresql+asyncpg://admin:admin1234@localhost:5432/test_taskpilot"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создает event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Создает тестовый движок БД."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очищаем после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Создает тестовую сессию БД."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создает тестовый HTTP клиент."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_settings() -> Settings:
    """Возвращает тестовые настройки."""
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        JWT_SECRET_KEY="test_secret_key_for_testing",
        REDIS_URL="redis://localhost:6379"
    )
