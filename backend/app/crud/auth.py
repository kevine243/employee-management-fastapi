from sqlalchemy import delete, select, update  # ← ajoute update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.models import User, EmailVerification, Department, PasswordResetToken
from uuid import UUID
from app.core.security import get_password_hash


async def create_reset_password_token(db: AsyncSession, email: str):
    id_query = await db.execute(select(User.id).where(User.email == email))
    id_result = id_query.scalar_one_or_none()

    if not id_result:
        raise ValueError("No user found with this email")

    token = PasswordResetToken(
        user_id=id_result,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        is_used=False,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


async def get_reset_password_token(
    db: AsyncSession, token: str
) -> PasswordResetToken | None:
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used.is_(False),
            PasswordResetToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def reset_password(db, user_id: UUID, new_password: str):
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(hashed_password=get_password_hash(new_password))
    )

    await db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user_id)
        .values(is_used=True)
    )
    await db.commit()





# class PasswordResetToken(Base):
#     __tablename__ = "password_reset_tokens"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     token = Column(String, unique=True, nullable=False)
#     expires_at = Column(DateTime(timezone=True), nullable=False)
#     is_used = Column(Boolean, default=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     user = relationship("User", back_populates="reset_tokens")

# sI2-SfFb8juyYY-NYGwCljl--ZzgDO6Z3eCsA-wZIyM
