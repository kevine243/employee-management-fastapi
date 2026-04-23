from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
)


async def send_confirmation_email(email: str, token: str):
    # ← pointe directement vers l'API FastAPI
    confirm_url = f"http://localhost:8000/api/v1/auth/confirm-email?token={token}"
    
    message = MessageSchema(
        subject="Confirm your email",
        recipients=[email],
        body=f"""
        <h2>Welcome!</h2>
        <p>Click the link below to confirm your email:</p>
        <a href="{confirm_url}">Confirm my email</a>
        <p>This link expires in 24h.</p>
        <br>
        <p>Or copy this URL in your browser:</p>
        <p>{confirm_url}</p>
        """,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)