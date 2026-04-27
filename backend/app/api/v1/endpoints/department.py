from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rbac import RoleChecker
from app.db.session import get_db
from app.crud.department import (
    get_all,
    create,
    get_department_by_id,
    update_department_partial,
    delete_dpt,
)
from app.schemas.departement import DepartmentRead, DepartmentCreate, DepartmentUpdate
from app.models.models import Department
from sqlalchemy import select, update
from app.core.rbac import RoleChecker
from app.models.models import User
from uuid import UUID
from sqlalchemy.orm import selectinload

from app.crud import department

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
current_user: User = Depends(RoleChecker(["admin", "editor"]))
):
    new_department = Department(name=request.name)
    created = await create(db, new_department)

    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Department already exists"
        )

    return created


@department_router.patch("/{department_id}/edit")
async def update_department_partial_route(
    request: DepartmentUpdate,
    department_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    update_data = request.model_dump(exclude_unset=True)

    updated = await update_department_partial(
        db=db,
        department_id=department_id,
        update_data=update_data,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return updated


@department_router.delete("/{department_id}/delete")
async def delete_department(
    department_id,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    delete = await delete_dpt(db, department_id)

    if not delete:
        raise (
            HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A department with this ID doesnt exists",
            )
        )
    return delete


@department_router.get("/{department_id}", response_model=DepartmentRead)
async def get_department_by_id_route(
    department_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    department = await get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return department
