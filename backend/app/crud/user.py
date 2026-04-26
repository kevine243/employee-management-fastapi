from sqlalchemy import delete, select, update  # ← ajoute update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.models import User, EmailVerification, Department
from uuid import UUID


# ── User ──────────────────────────────────────────


# by uuid
async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_all_user(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User).options(selectinload(User.roles), selectinload(User.department))
    )
    users = result.scalars().all()
    return list(users)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ── Email Verification ────────────────────────────


async def create_verification_token(
    db: AsyncSession, user_id: UUID, type: str = "email_confirm"
) -> EmailVerification:
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
async def get_verification_token(
    db: AsyncSession, token: str
) -> EmailVerification | None:
    result = await db.execute(
        select(EmailVerification)
        # .options(selectinload(EmailVerification.user))  ← plus nécessaire
        .where(
            EmailVerification.token == token,
            EmailVerification.is_used.is_(False),
            EmailVerification.expires_at > datetime.now(timezone.utc),
            EmailVerification.type == "email_confirm",
        )
    )
    return result.scalar_one_or_none()


async def verify_user(
    db: AsyncSession, user_id: UUID, token: EmailVerification
) -> None:

    await db.execute(
        update(User).where(User.id == user_id).values(is_verified=True, is_active=True)
    )

    await db.execute(
        update(EmailVerification)
        .where(EmailVerification.id == token.id)
        .values(is_used=True)
    )

    await db.commit()


async def update_user_partial(
    db: AsyncSession,
    user_id: UUID,
    update_data: dict,
) -> User | None:

    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles),
            selectinload(User.department),
        )
        .where(User.id == user_id)
    )

    existing = result.scalar_one_or_none()

    if not existing:
        return None

    if existing.roles and "admin" in [role.name for role in existing.roles]:
        raise ValueError("Cannot modify an admin user")

    # 🔥 check department
    if "department_id" in update_data and update_data["department_id"]:
        dept_result = await db.execute(
            select(Department).where(Department.id == update_data["department_id"])
        )

        department = dept_result.scalar_one_or_none()

        if not department:
            raise ValueError("Department not found")

    excluded_fields = {
        "id",
        "created_at",
        "updated_at",
        "roles",
        "department",
        "verifications",
        "hashed_password",
    }

    for field, value in update_data.items():
        if field not in excluded_fields and value is not None:
            setattr(existing, field, value)

    await db.commit()
    await db.refresh(existing)

    return existing


async def delete_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(User).where(User.id == user_id))
    existing = result.scalar_one_or_none()

    if not existing:
        return None

    await db.delete(existing)  # ← supprime user + verifications automatiquement
    await db.commit()
    return {"message": f"User {user_id} deleted successfully"}
