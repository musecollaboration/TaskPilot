from dataclasses import dataclass

from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError

from app.settings import Settings


@dataclass
class YandexAuthClient:
    settings: Settings

    async def get_user_info(self, code: str) -> dict:
        """        
        Получает информацию о пользователе из Yandex по коду авторизации.
        Возвращает информацию о пользователе в виде словаря.
        """
        try:
            access_token = await self.get_user_access_token(code)
            headers = {'Authorization': f'OAuth {access_token}'}
            async with AsyncClient() as client:
                response = await client.get(self.settings.YANDEX_USER_INFO_URL, headers=headers)
                response.raise_for_status()
                user_info = response.json()
            if not user_info or 'default_email' not in user_info:
                raise HTTPException(status_code=400, detail="Некорректный ответ от Yandex: нет email")
            return user_info
        except HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка Yandex API: {e.response.text}")
        except RequestError as e:
            raise HTTPException(status_code=503, detail=f"Ошибка сети при обращении к Yandex: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка авторизации: {str(e)}")

    async def get_user_access_token(self, code: str) -> str:
        """        
        Получает токен доступа пользователя по коду авторизации.
        Возвращает токен доступа в виде строки.
        """
        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                'code': code,
                'client_id': self.settings.YANDEX_CLIENT_ID,
                'client_secret': self.settings.YANDEX_CLIENT_SECRET,
                'redirect_uri': self.settings.YANDEX_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            async with AsyncClient() as client:
                response = await client.post(
                    self.settings.YANDEX_TOKEN_URL,
                      data=data,
                      headers=headers
                )
                response.raise_for_status()
                token_data = response.json()
                access_token = token_data.get('access_token')
                if not access_token:
                    raise HTTPException(status_code=401, detail="Yandex не вернул access_token")
                return access_token

        except HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка получения токена: {e.response.text}")
        except RequestError as e:
            raise
