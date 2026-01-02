from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Task Pilot"           # Название приложения
    APP_VERSION: str = "1.0.0"             # Версия приложения
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/taskpilot"
    API_VERSION_PREFIX: str = "/api/v1"    # Версия API в путях

    # Redis настройки
    REDIS_URL: str = "redis://localhost:6379"

    # JWT настройки
    JWT_SECRET_KEY: str = "change_me_to_secure_secret_key"   # Секретный ключ для JWT
    JWT_ALGORITHM: str = "HS256"          # Алгоритм шифрования

    # OAuth2 настройки
    GOOGLE_CLIENT_ID: str = "your_google_client_id"
    GOOGLE_CLIENT_SECRET: str = "your_google_client_secret"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/login/google/callback"
    GOOGLE_TOKEN_URL: str = "https://accounts.google.com/o/oauth2/token"
    GOOGLE_USER_INFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"

    YANDEX_CLIENT_ID: str = "your_yandex_client_id"
    YANDEX_CLIENT_SECRET: str = "your_yandex_client_secret"
    YANDEX_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/login/yandex/callback"
    YANDEX_TOKEN_URL: str = "https://oauth.yandex.ru/token"
    YANDEX_USER_INFO_URL: str = "https://login.yandex.ru/info"

    VK_CLIENT_ID: str = "your_vk_client_id"
    VK_CLIENT_SECRET: str = "your_vk_client_secret"
    VK_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/login/vk/callback"
    VK_AUTH_URL: str = "https://oauth.vk.com/authorize"
    VK_TOKEN_URL: str = "https://oauth.vk.com/access_token"
    VK_USER_INFO_URL: str = "https://api.vk.com/method/users.get"
    VK_API_VERSION: str = "5.131"

    # Email (SMTP) настройки
    GMAIL_SMTP_HOST: str = "smtp.gmail.com"
    GMAIL_SMTP_PORT: int = 587
    GMAIL_ADDRESS: str = 'your_email@gmail.com'
    GMAIL_APP_PASSWORD: str = 'your_gmail_app_password'

    class Config:
        env_file = ".env"             # Файл окружения для настроек
        env_file_encoding = "utf-8"   # Кодировка файла окружения


settings = Settings()
