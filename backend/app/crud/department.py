from sqlalchemy import select, update  # ← ajoute update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Department
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from uuid import UUID


async def get_all(db: AsyncSession):
    result = await db.execute(
        select(Department).options(selectinload(Department.users))
    )
    return result.scalars().all()


async def create(db: AsyncSession, department: Department):
    query = await db.execute(
        select(Department).where(Department.name == department.name)
    )
    existing = query.scalar_one_or_none()

    if existing:
        return None

    db.add(department)
    await db.commit()
    await db.refresh(department)
    return department


async def update_department_partial(
    db: AsyncSession,
    department_id: UUID,
    update_data: dict,
):
    result = await db.execute(select(Department).where(Department.id == department_id))
    existing = result.scalar_one_or_none()

    if not existing:
        return None

    for field, value in update_data.items():
        if hasattr(existing, field):
            setattr(existing, field, value)

    await db.commit()
    await db.refresh(existing)

    return existing


async def delete_dpt(db: AsyncSession, department_id: UUID):
    result = await db.execute(select(Department).where(Department.id == department_id))
    existing = result.scalar_one_or_none()

    if not existing:
        return None
    await db.delete(existing)
    await db.commit()
    return existing


async def get_department_by_id(db: AsyncSession, department_id: UUID):
    result = await db.execute(
        select(Department)
        .options(selectinload(Department.users))
        .where(Department.id == department_id)
    )
    return result.scalar_one_or_none()
