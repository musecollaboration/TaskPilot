from dataclasses import dataclass

from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError

from app.settings import Settings


@dataclass
class VKAuthClient:
    settings: Settings

    async def get_user_access_token(self, code: str, code_verifier: str) -> dict:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.VK_REDIRECT_URI,
            "client_id": self.settings.VK_CLIENT_ID,
            "code_verifier": code_verifier,
        }
        async with AsyncClient() as client:
            try:
                response = await client.post("https://id.vk.com/oauth2/token", data=data)
                response.raise_for_status()
                token_data = response.json()
                if "error" in token_data:
                    raise HTTPException(status_code=400, detail=token_data.get("error_description", "VK error"))
                return token_data
            except (HTTPStatusError, RequestError) as e:
                raise HTTPException(status_code=503, detail=f"Ошибка VK: {str(e)}")

    async def get_user_info(self, access_token: str, user_id: str) -> dict:
        params = {
            "user_ids": user_id,
            "fields": "photo_100,city,verified",
            "access_token": access_token,
            "v": self.settings.VK_API_VERSION,
        }
        async with AsyncClient() as client:
            try:
                response = await client.get("https://api.vk.com/method/users.get", params=params)
                response.raise_for_status()
                data = response.json()
                if "error" in data:
                    raise HTTPException(status_code=400, detail=data["error"]["error_msg"])
                return data["response"][0]
            except (HTTPStatusError, RequestError) as e:
                raise HTTPException(status_code=503, detail=f"Ошибка VK: {str(e)}")
