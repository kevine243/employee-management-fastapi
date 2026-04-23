# app/scripts/seed.py
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import User, Role, RoleEnum
from app.core.security import get_password_hash


async def seed():
    async with AsyncSessionLocal() as db:
        # Crée les rôles s'ils n'existent pas
        for role_enum in RoleEnum:
            existing = await db.execute(
                select(Role).where(Role.name == role_enum)
            )
            if not existing.scalar_one_or_none():
                db.add(Role(name=role_enum))
        
        await db.commit()

        # Crée le premier admin
        existing_admin = await db.execute(
            select(User).where(User.email == "admin@test.com")
        )
        if not existing_admin.scalar_one_or_none():
            admin_role = await db.execute(
                select(Role).where(Role.name == RoleEnum.admin)
            )
            admin_role = admin_role.scalar_one()

            admin = User(
                email="admin@test.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_verified=True,
            )
            admin.roles.append(admin_role)
            db.add(admin)
            await db.commit()
            print("✅ Admin créé : admin@test.com / admin123")
        else:
            print("ℹ️ Admin existe déjà")

if __name__ == "__main__":
    asyncio.run(seed())
    
# uv run python -m app.scripts.seed