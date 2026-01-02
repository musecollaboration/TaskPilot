import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

import redis.asyncio as redis_async
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.auth_service import AuthService
from app.database.dependencies import get_auth_service, get_user_service
from app.schema.user import UserRead
from app.service.user import UserService
from app.settings import settings


# Инициализация клиента Redis
redis = redis_async.from_url(settings.REDIS_URL)

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post(
    "/login",
    status_code=200,
    summary="Вход в систему",
    description="Эндпоинт для входа в систему с использованием учетных данных пользователя."
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    expires_minutes: Annotated[int, Query(
        description="Время жизни токена в минутах",
        alias="minutes",
        ge=1,
        le=2880)] = 15
):
    """
    Эндпоинт для запроса на вход в систему.
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    # Создание JWT токена
    access_token = await auth_service.create_jwt_for_user(
        user=user,
        expires_delta=expires_minutes
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/confirm-email",
    status_code=200,
    summary="Подтверждение email",
    description="Эндпоинт для подтверждения email пользователя.",
    response_model=UserRead
)
async def confirm_email(
        token: Annotated[str, Query(description="Токен подтверждения email")],
        user_service: Annotated[UserService, Depends(get_user_service)]
):
    """
    Эндпоинт для подтверждения email пользователя.
    """
    user_id = await redis.get(f"email_confirm:{token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Токен недействителен или истёк")
    user_id = UUID(user_id.decode())
    user = await user_service.activate_user(user_id)
    await redis.delete(f"email_confirm:{token}")
    return user


@router.get(
    "/login/google",
    summary="Вход через Google",
    description="Эндпоинт для перенаправления пользователя на страницу авторизации Google."
)
async def login_google(
):
    """
    Эндпоинт для перенаправления пользователя на страницу авторизации Google.
    """
    # Генерация безопасного state
    state = hashlib.sha256(os.urandom(64)).hexdigest()

    # Формируем данные для хранения
    state_data = json.dumps({
        "state": state,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    # Сохраняем state в Redis с TTL 5 минут
    await redis.set(
        f"oauth_state:{state}",  # ключ
        state_data,              # значение
        ex=300                   # TTL в секундах
    )

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&scope=openid%20profile%20email"
        f"&access_type=offline"
        f"&state={state}"
    )
    print("Google OAuth2 URL:", google_auth_url)
    return RedirectResponse(url=google_auth_url)


@router.get(
    "/login/google/callback",
    status_code=200,
    summary="Колбэк после авторизации через Google",
    description="Эндпоинт для обработки колбэка после авторизации пользователя через Google."
)
async def google_callback(
    code: Annotated[str, Query(description="Код авторизации, полученный от Google")],
    state: Annotated[str, Query(description="Состояние для защиты от CSRF")],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Эндпоинт для обработки колбэка после авторизации через Google.
    Получает код авторизации, обменивает его на токен доступа и создает JWT для пользователя.
    """

    raw_data = await redis.get(f"oauth_state:{state}")
    # Проверка наличия state
    if not raw_data:
        raise HTTPException(status_code=400, detail="State не найден или истёк")

    data = json.loads(raw_data)

    # Проверка соответствия
    if data["state"] != state:
        raise HTTPException(status_code=400, detail="Некорректный state")

    # (опционально) проверка времени жизни
    created_at = datetime.fromisoformat(data["created_at"])
    age = (datetime.now(timezone.utc) - created_at).total_seconds()
    if age > 300:
        raise HTTPException(status_code=400, detail="State просрочен")

    await redis.delete(f"oauth_state:{state}")
    user = await auth_service.authenticate_google_user(code)
    access_token = await auth_service.create_jwt_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/login/yandex",
    summary="Вход через Yandex",
    description="Эндпоинт для перенаправления пользователя на страницу авторизации Yandex."
)
async def login_yandex(
):
    """
    Эндпоинт для перенаправления пользователя на страницу авторизации Yandex.
    """
    # Генерация безопасного state
    state = hashlib.sha256(os.urandom(64)).hexdigest()

    # Формируем данные для хранения
    state_data = json.dumps({
        "state": state,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    # Сохраняем state в Redis с TTL 5 минут
    await redis.set(
        f"oauth_state:{state}",  # ключ
        state_data,              # значение
        ex=300                   # TTL в секундах
    )

    yandex_auth_url = (
        f"https://oauth.yandex.com/authorize"
        f"?response_type=code"
        f"&client_id={settings.YANDEX_CLIENT_ID}"
        f"&redirect_uri={settings.YANDEX_REDIRECT_URI}"
        f"&scope=login:avatar%20login:birthday%20login:email%20login:info%20login:default_phone"
        f"&state={state}"
    )
    print("Yandex OAuth2 URL:", yandex_auth_url)
    return RedirectResponse(url=yandex_auth_url)


@router.get(
    "/login/yandex/callback",
    status_code=200,
    summary="Колбэк после авторизации через Yandex",
    description="Эндпоинт для обработки колбэка после авторизации пользователя через Yandex."
)
async def yandex_callback(
    code: Annotated[str, Query(description="Код авторизации, полученный от Yandex")],
    state: Annotated[str, Query(description="Состояние для защиты от CSRF")],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Эндпоинт для обработки колбэка после авторизации через Yandex.
    Получает код авторизации, обменивает его на токен доступа и создает JWT для пользователя.
    """
    raw_data = await redis.get(f"oauth_state:{state}")
    # Проверка наличия state
    if not raw_data:
        raise HTTPException(status_code=400, detail="State не найден или истёк")

    data = json.loads(raw_data)

    # Проверка соответствия
    if data["state"] != state:
        raise HTTPException(status_code=400, detail="Некорректный state")

    # (опционально) проверка времени жизни
    created_at = datetime.fromisoformat(data["created_at"])
    age = (datetime.now(timezone.utc) - created_at).total_seconds()
    if age > 300:
        raise HTTPException(status_code=400, detail="State просрочен")

    await redis.delete(f"oauth_state:{state}")
    user = await auth_service.authenticate_yandex_user(code)
    access_token = await auth_service.create_jwt_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}


def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')


# ngrok http 8000
# https://2abedfb331a1.ngrok-free.app/api/v1/docs#/

@router.get("/login/vk")
async def login_vk():
    state = hashlib.sha256(os.urandom(64)).hexdigest()
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    state_data = json.dumps({
        "state": state,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code_verifier": code_verifier
    })
    await redis.set(f"oauth_state:{state}", state_data, ex=300)
    vk_auth_url = (
        f"https://id.vk.com/authorize"
        f"?response_type=code"
        f"&client_id={settings.VK_CLIENT_ID}"
        f"&redirect_uri={settings.VK_REDIRECT_URI}"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&scope=email"
    )
    print("VK OAuth2 URL:", vk_auth_url)
    return RedirectResponse(url=vk_auth_url)


@router.get("/login/vk/callback")
async def vk_callback(
    code: Annotated[str, Query(description="Код авторизации VK")],
    state: Annotated[str, Query(description="Состояние для защиты от CSRF")],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    raw_data = await redis.get(f"oauth_state:{state}")
    if not raw_data:
        raise HTTPException(status_code=400, detail="State не найден или истёк")
    data = json.loads(raw_data)
    if data["state"] != state:
        raise HTTPException(status_code=400, detail="Некорректный state")
    code_verifier = data["code_verifier"]
    created_at = datetime.fromisoformat(data["created_at"])
    age = (datetime.now(timezone.utc) - created_at).total_seconds()
    if age > 300:
        raise HTTPException(status_code=400, detail="State просрочен")
    await redis.delete(f"oauth_state:{state}")
    user = await auth_service.authenticate_vk_user(code, code_verifier)
    access_token = await auth_service.create_jwt_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}
