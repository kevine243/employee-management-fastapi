from sqlalchemy import select, update  # ← ajoute update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Department
from sqlalchemy.orm import selectinload
from fastapi import HTTPException,status

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