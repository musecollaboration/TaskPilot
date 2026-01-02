from dataclasses import dataclass

from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError

from app.settings import Settings


@dataclass
class GoogleAuthClient:
    settings: Settings

    async def get_user_info(self, code: str) -> dict:
        """        
        Получает информацию о пользователе из Google по коду авторизации.
        Возвращает информацию о пользователе в виде словаря.
        """
        try:
            access_token = await self.get_user_access_token(code)
            headers = {'Authorization': f'Bearer {access_token}'}
            async with AsyncClient() as client:
                response = await client.get(self.settings.GOOGLE_USER_INFO_URL, headers=headers)
                response.raise_for_status()
                user_info = response.json()
            if not user_info or 'email' not in user_info:
                raise HTTPException(status_code=400, detail="Некорректный ответ от Google: нет email")
            return user_info
        except HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка Google API: {e.response.text}")
        except RequestError as e:
            raise HTTPException(status_code=503, detail=f"Ошибка сети при обращении к Google: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка авторизации: {str(e)}")

    async def get_user_access_token(self, code: str) -> str:
        """        
        Получает токен доступа пользователя по коду авторизации.
        Возвращает токен доступа в виде строки.
        """
        try:
            data = {
                'code': code,
                'client_id': self.settings.GOOGLE_CLIENT_ID,
                'client_secret': self.settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': self.settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            async with AsyncClient() as client:
                response = await client.post(self.settings.GOOGLE_TOKEN_URL, data=data)
                response.raise_for_status()
                token_data = response.json()
                access_token = token_data.get('access_token')
                if not access_token:
                    raise HTTPException(status_code=401, detail="Google не вернул access_token")
                return access_token

        except HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка получения токена: {e.response.text}")
        except RequestError as e:
            raise HTTPException(status_code=503, detail=f"Ошибка сети при получении токена: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка получения токена: {str(e)}")
