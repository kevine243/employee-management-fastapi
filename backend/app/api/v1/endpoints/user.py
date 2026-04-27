from asyncio import wait

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rbac import RoleChecker
from app.db.session import get_db
from app.crud.user import (
    change_password,
    get_all_user,
    get_user_by_id,
    get_user_with_relations,
    remove_profile_picture_from_files,
    update_user_partial,
    update_profile_picture,
)
from app.schemas.user import (
    ChangePassword,
    UserDashboard,
    UserBase,
    UserMe,
    UserUpdate,
    UserRead,
    UserCreate,
)
from app.core.rbac import RoleChecker
from app.models.models import User
from uuid import UUID
from app.crud.user import create_user as crud_create_user
from app.core.security import get_password_hash, verify_password
from app.crud.user import get_user_by_email, create_verification_token
from app.services.email import send_confirmation_email, send_password_reset_mail
from app.crud.user import delete_user
from app.dependencies import get_current_active_user
from app.crud.role import get_roles, assign_role_to_user, remove_role_from_user

# upload user profile picture endpoint to be added later
import aiofiles
import uuid
from fastapi import UploadFile, File
from pathlib import Path

UPLOAD_DIR = Path("static/profile_pictures")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 2 * 1024 * 1024  # 2MB

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


@user_router.get("/me", response_model=UserMe)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


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


@user_router.patch("/{user_id}/edit", response_model=UserDashboard)
async def update_user_partial_route(
    request: UserUpdate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "editor"])),
):
    update_data = request.model_dump(exclude_unset=True)

    try:
        updated = await update_user_partial(
            db=db,
            user_id=user_id,
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


@user_router.put("/me/password")
async def change_password_endpoint(
    request: ChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Vérifie l'ancien mot de passe
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    await change_password(db, current_user.id, request.new_password)
    return {"message": "Password changed successfully"}


@user_router.put("/{user_id}/roles/{role_id}", response_model=UserDashboard)
async def assign_role_to_user_endpoint(
    user_id: UUID,
    role_id: UUID,  # ← vient du path
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    try:
        return await assign_role_to_user(db, user_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.delete("/{user_id}/roles/{role_id}", response_model=UserDashboard)
async def remove_role_from_user_endpoint(
    user_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    try:
        return await remove_role_from_user(db, user_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post("/me/avatar", response_model=UserMe)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Only JPEG, PNG and WebP images are allowed"
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size must be less than 2MB")

    # 1. Génère le nouveau fichier
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    filepath = UPLOAD_DIR / filename

    # 2. Sauvegarde le nouveau fichier D'ABORD
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    # 3. Met à jour en DB
    old_picture = current_user.profile_picture  # ← garde l'ancien nom
    await update_profile_picture(db, current_user.id, filename)

    # 4. Supprime l'ancien fichier APRÈS succès
    if old_picture:
        old_file = UPLOAD_DIR / old_picture
        if old_file.exists():
            old_file.unlink()  # ← supprime seulement si tout s'est bien passé

    return await get_user_with_relations(db, current_user.id)  # ← recharge le user
