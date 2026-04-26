from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rbac import RoleChecker
from app.db.session import get_db
from app.crud.user import get_all_user, get_user_by_id, update_user_partial
from app.schemas.user import UserDashboard, UserBase, UserUpdate, UserRead, UserCreate
from app.core.rbac import RoleChecker
from app.models.models import User
from uuid import UUID
from app.crud.user import create_user as crud_create_user
from app.core.security import get_password_hash
from app.crud.user import get_user_by_email, create_verification_token
from app.services.email import send_confirmation_email
from app.crud.user import delete_user

user_router = APIRouter()


@user_router.post(
    "/create_user", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def create_user(
    background_tasks: BackgroundTasks,
    request: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    existing_user = await get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Address already registered",
        )

    hashed_password = get_password_hash(request.password)
    new_user = User(
        username=request.username, email=request.email, hashed_password=hashed_password
    )
    created_user = await crud_create_user(db, new_user)

    # Envoie email de confirmation
    verification = await create_verification_token(db, created_user.id)

    background_tasks.add_task(
        send_confirmation_email, created_user.email, verification.token
    )

    return created_user


@user_router.get("/", response_model=list[UserDashboard])
async def get_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    users = await get_all_user(db)
    return users


@user_router.get("/{user_id}", response_model=UserDashboard)
async def get_user_by_id_route(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@user_router.patch("/{user}/edit", response_model=UserDashboard)
async def update_user_partial_route(
    request: UserUpdate,
    user: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    update_data = request.model_dump(exclude_unset=True)

    try:
        updated = await update_user_partial(
            db=db,
            user_id=user,
            update_data=update_data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    return updated


@user_router.delete("/{user_id}/delete")
async def delete_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    delete = await delete_user(db, user_id)

    if not delete:
        raise (
            HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A user with this ID doesnt exists",
            )
        )
    return delete
