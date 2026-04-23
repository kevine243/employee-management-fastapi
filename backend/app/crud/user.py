from sqlalchemy import select, update  # ← ajoute update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.orm import selectinload

from app.models.models import User, EmailVerification

# ── User ──────────────────────────────────────────

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# ── Email Verification ────────────────────────────

async def create_verification_token(db: AsyncSession, user_id: int, type: str = "email_confirm") -> EmailVerification:
    token = EmailVerification(
        user_id=user_id,
        token=secrets.token_urlsafe(32),
        type=type,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token

# On n'accède plus à verification.user donc plus besoin de selectinload
async def get_verification_token(db: AsyncSession, token: str) -> EmailVerification | None:
    result = await db.execute(
        select(EmailVerification)
        # .options(selectinload(EmailVerification.user))  ← plus nécessaire
        .where(
            EmailVerification.token == token,
            EmailVerification.is_used.is_(False),
            EmailVerification.expires_at > datetime.now(timezone.utc),
            EmailVerification.type == "email_confirm"
        )
    )
    return result.scalar_one_or_none()

async def verify_user(db: AsyncSession, user_id: int, token: EmailVerification) -> None:
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_verified=True, is_active=True)
    )
    token.is_used = True
    await db.commit()
    