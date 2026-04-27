from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Role, User
from app.crud.user import get_user_with_relations
from sqlalchemy.orm import selectinload


async def assign_role_to_user(db: AsyncSession, user_id: UUID, role_id: UUID):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    result_role = await db.execute(select(Role).where(Role.id == role_id))
    role = result_role.scalar_one_or_none()
    if not role:
        raise ValueError("Role not found")

    if role in user.roles:
        raise ValueError(f"Role already assigned to this user")

    user.roles.append(role)
    await db.commit()
    return await get_user_with_relations(db, user_id)  # ← recharge proprement


async def get_roles(db: AsyncSession) -> list[Role]:
    result = await db.execute(select(Role))
    return result.scalars().all()


async def remove_role_from_user(db: AsyncSession, user_id: UUID, role_id: UUID):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    result_role = await db.execute(select(Role).where(Role.id == role_id))
    role = result_role.scalar_one_or_none()
    if not role:
        raise ValueError("Role not found")

    if role not in user.roles:
        raise ValueError(f"Role not assigned to this user")

    user.roles.remove(role)
    await db.commit()
    return await get_user_with_relations(db, user_id)
