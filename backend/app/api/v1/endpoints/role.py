from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rbac import RoleChecker
from app.db.session import get_db
from app.crud.role import assign_role_to_user, get_roles, remove_role_from_user
from app.schemas.user import RoleRead, UserDashboard
from app.models.models import User
from uuid import UUID

from app.crud.user import get_user_by_id

role_router = APIRouter(prefix="/roles", tags=["roles"])


@role_router.get("/", response_model=list[RoleRead])
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    return await get_roles(db)


