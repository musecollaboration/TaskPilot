from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.settings import settings


def create_access_token(data: dict, expires_delta: timedelta):
    '''
    Создает JWT токен с заданными данными и временем истечения.
    Если expires_delta не указан, токен будет действителен 15 минут.
    '''
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str):
    '''
    Декодирует JWT токен и возвращает его содержимое.
    Если токен недействителен, возвращает None.
    '''
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM])
        return payload

    except JWTError:
        return None
