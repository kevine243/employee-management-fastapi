from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.crud.user import (
    create_user as crud_create_user,
    get_user_by_email,
    create_verification_token,
)
from app.core.rbac import RoleChecker
from app.services.email import send_confirmation_email
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.user import get_verification_token, verify_user

# from sqlalchemy.dialects.postgresql import UUID  # Si tu utilises PostgreSQL
from uuid import UUID

# Si tu utilises une base de données qui supporte UUID, sinon adapte en conséquence

auth_router = APIRouter()


@auth_router.post(
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
    new_user = User(email=request.email, hashed_password=hashed_password)
    created_user = await crud_create_user(db, new_user)

    # Envoie email de confirmation
    verification = await create_verification_token(db, created_user.id)

    background_tasks.add_task(
        send_confirmation_email, created_user.email, verification.token
    )

    return created_user


@auth_router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # ← vérifie que l'email est confirmé
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please confirm your email before logging in",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/confirm-email")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):

    verification = await get_verification_token(db, token)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    await verify_user(
        db, verification.user_id, verification
    )  # ← user_id pas verification.user
    return {"message": "Email confirmed successfully"}
