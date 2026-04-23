from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rbac import RoleChecker
from app.db.session import get_db
from app.crud.department import get_all, create
from app.schemas.departement import DepartmentRead, DepartmentCreate
from app.models.models import Department
from sqlalchemy import select, update
from app.core.rbac import RoleChecker
from app.models.models import User

department_router = APIRouter()


@department_router.get("/all", response_model=list[DepartmentRead])
async def get_all_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    departments = await get_all(db)
    if not departments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There are not Departments"
        )
    return departments


@department_router.post("/create")
async def create_department(
    request: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    new_department = Department(name=request.name)
    created = await create(db, new_department)

    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Department already exists"
        )

    return created
