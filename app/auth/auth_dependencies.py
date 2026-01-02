from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_access_token
from app.database.models.user import User
from app.database.session import get_db
from app.repositories.user import UserRepository


security = HTTPBearer()


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """
    Получить текущего пользователя из JWT токена.
    Если токен недействителен или пользователь не найден, выбрасывает HTTPException.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    user_id = UUID(payload["sub"])
    user_repository = UserRepository(db)
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Пользователь не активен")
    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user
