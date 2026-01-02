from dataclasses import dataclass
from uuid import UUID

from app.auth.auth_service import AuthService
from app.repositories.user import UserRepository
from app.schema.user import UserCreate
from app.service.email import send_confirmation_email


@dataclass
class UserService:
    user_repository: UserRepository
    auth_service: AuthService

    async def register_user(self, user_schema: UserCreate):
        """
        Регистрация нового пользователя.
        Хеширует пароль и сохраняет пользователя в базе данных.
        """
        user_data = user_schema.model_dump()
        password = user_data.pop('password').get_secret_value()
        hash_password = await self.auth_service.hash_password(
            password=password
        )
        user_data['hashed_password'] = hash_password
        user = await self.user_repository.create_user(
            user_data=user_data
        )
        # Генерация токена подтверждения email
        token = await self.auth_service.create_email_confirmation_token()

        await send_confirmation_email(user.email, token)
        return user, token

    async def activate_user(self, user_id: UUID):
        """
        Активация пользователя по его идентификатору.
        """
        user = await self.get_user_by_id(user_id)
        await self.user_repository.update_user(
            user=user,
            user_data={"is_active": True}
        )
        return user

    async def get_user_by_id(self, user_id: UUID):
        """
        Получение пользователя по ID пользователя.
        """
        return await self.user_repository.get_user_by_id(user_id=user_id)
