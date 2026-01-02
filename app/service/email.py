from email.message import EmailMessage

import aiosmtplib

from app.settings import settings


async def send_confirmation_email(to_email: str, token: str):
    msg = EmailMessage()
    msg["From"] = "noreply@localhost"
    msg["To"] = to_email
    msg["Subject"] = "Подтверждение регистрации"
    confirm_url = f"http://localhost:8000/api/v1/auth/confirm-email?token={token}"
    msg.set_content(
        f"Для подтверждения регистрации перейдите по ссылке: {confirm_url}"
        f"\nСсылка действительна в течение 12 часов."
        f"\nЕсли вы не регистрировались, просто проигнорируйте это письмо."
    )

    await aiosmtplib.send(
        msg,
        hostname=settings.GMAIL_SMTP_HOST,     # SMTP-сервер Gmail
        port=settings.GMAIL_SMTP_PORT,         # порт для TLS
        username=settings.GMAIL_ADDRESS,       # твой Gmail адрес
        password=settings.GMAIL_APP_PASSWORD,  # пароль приложения Gmail
        start_tls=True                         # использовать TLS
    )
