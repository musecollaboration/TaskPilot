from dataclasses import dataclass
from datetime import timedelta

from passlib.context import CryptContext

from app.auth.client.google import GoogleAuthClient
from app.auth.client.vk import VKAuthClient
from app.auth.client.yandex import YandexAuthClient
from app.auth.jwt import create_access_token, decode_access_token
from app.database.models.user import User
from app.repositories.user import UserRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class AuthService:
    user_repository: UserRepository
    google_client: GoogleAuthClient
    yandex_client: YandexAuthClient
    vk_client: VKAuthClient

    async def authenticate_user(self, username: str, password: str):
        """
        Аутентифицировать пользователя по имени пользователя и паролю.
        Возвращает пользователя, если аутентификация успешная, иначе None.
        """
        user: User = await self.user_repository.get_by_username(
            username=username
        )
        if user and await self.verify_password(password, user.hashed_password):
            return user
        return None

    async def hash_password(self, password: str) -> str:
        """        
        Хеширует пароль с использованием bcrypt.
        Возвращает хешированный пароль.
        """
        return pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Проверяет, соответствует ли введенный пароль хешированному паролю.
        Возвращает True, если пароли совпадают, иначе False.
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def create_jwt_for_user(self, user: User, expires_delta: int = 15):
        """
        Создает JWT для пользователя.
        Возвращает JWT в виде строки.
        """
        return create_access_token(
            {"sub": str(user.id)},
            expires_delta=timedelta(minutes=expires_delta)
        )

    async def decode_jwt(self, token: str):
        """
        Декодирует JWT и возвращает его содержимое.        
        """
        return decode_access_token(token=token)

    async def authenticate_google_user(self, code: str) -> User:
        """
        Аутентифицирует пользователя через Google OAuth2.
        Возвращает пользователя, если аутентификация успешна, иначе создает нового пользователя
        с данными из Google.
        """

        user_info = await self.google_client.get_user_info(code)
        email = user_info["email"]
        user = await self.user_repository.get_by_email(email)
        if not user:
            # Если пользователь не найден, создаем нового пользователя
            username = f'google_{email.split("@")[0]}'
            user_data = {
                "username": username,
                "email": email,
                "hashed_password": "",
                "is_active": True,
                "is_admin": False,
            }
            user = await self.user_repository.create_user(user_data)
        return user

    async def authenticate_yandex_user(self, code: str) -> User:
        """
        Аутентифицирует пользователя через Yandex OAuth2.
        Возвращает пользователя, если аутентификация успешна, иначе создает нового пользователя
        с данными из Yandex.
        """

        user_info = await self.yandex_client.get_user_info(code)
        email = user_info["default_email"]
        user = await self.user_repository.get_by_email(email)
        if not user:
            # Если пользователь не найден, создаем нового пользователя
            username = f'yandex_{email.split("@")[0]}'
            user_data = {
                "username": username,
                "email": email,
                "hashed_password": "",
                "is_active": True,
                "is_admin": False,
            }
            user = await self.user_repository.create_user(user_data)
        return user

    async def create_email_confirmation_token(self):
        """
        Создает токен для подтверждения email.
        """
        return create_access_token(
            {"sub": "email_confirmation"},
            expires_delta=timedelta(hours=12)
        )

    async def authenticate_vk_user(self, code: str, code_verifier: str):
        token_data = await self.vk_client.get_user_access_token(code, code_verifier)
        access_token = token_data["access_token"]
        user_id = str(token_data["user_id"])
        user_info = await self.vk_client.get_user_info(access_token, user_id)
        username = user_info.get("first_name", "") + " " + user_info.get("last_name", "")
        email = token_data.get("email", f"{user_id}@vk.com")
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            user_data = {
                "username": username,
                "email": email,
                "hashed_password": "",
                "is_active": True,
                "is_admin": False,
            }
            user = await self.user_repository.create_user(user_data)
        return user
