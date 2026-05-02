from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import User
from app.schemas.user import (
    UserCreate,
    UserRead,
    EmailReset,
    PasswordReset,
)
from app.schemas.token import TokenPair, RefreshTokenRequest, Token

from app.core.security import get_password_hash, verify_password, create_access_token
from app.crud.user import (
    create_refresh_token,
    create_user as crud_create_user,
    get_user_by_email,
    create_verification_token,
    revoke_refresh_token,
    get_refresh_token,
)
from app.crud.auth import (
    create_reset_password_token,
    get_reset_password_token,
    reset_password,
)
from app.core.rbac import RoleChecker
from app.services.email import send_confirmation_email, send_password_reset_mail
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.user import get_verification_token, verify_user

# from sqlalchemy.dialects.postgresql import UUID  # Si tu utilises PostgreSQL
from uuid import UUID

from app.dependencies import get_current_user

# Si tu utilises une base de données qui supporte UUID, sinon adapte en conséquence

auth_router = APIRouter()


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
    refresh_token = await create_refresh_token(db, user.id)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token.token,
        token_type="bearer",
    )


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


@auth_router.post("/forgot-password")
async def create_password_reset_endpoint(
    background_task: BackgroundTasks,
    formdata: EmailReset,
    db: AsyncSession = Depends(get_db),
):
    try:
        token = await create_reset_password_token(db, formdata.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    get_token = await get_reset_password_token(db, token.token)
    if not get_token:
        raise HTTPException(
            status_code=400, detail="something is wrong or the token is invalid"
        )
    background_task.add_task(send_password_reset_mail, formdata.email, get_token.token)

    return {"message": "a reset password link has been sent to your mail"}


# GET — vérifie le token quand le user clique sur le lien
@auth_router.get("/reset-password")
async def verify_reset_token(token: str, db: AsyncSession = Depends(get_db)):
    existing_token = await get_reset_password_token(db, token)
    if not existing_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )
    # Retourne juste le token pour que le frontend l'utilise dans le formulaire
    return {"token": token, "message": "Token valid, you can reset your password"}


# POST — change le mot de passe
@auth_router.post("/reset-password")
async def reset_password_endpoint(
    request: PasswordReset,
    db: AsyncSession = Depends(get_db),
):
    existing_token = await get_reset_password_token(db, request.token)
    if not existing_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    await reset_password(db, existing_token.user_id, request.new_password)
    return {"message": "Password reset successfully"}


@auth_router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    token = await get_refresh_token(db, request.refresh_token)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Rotation du refresh token — révoque l'ancien, crée un nouveau
    await revoke_refresh_token(db, request.refresh_token)
    new_refresh_token = await create_refresh_token(db, token.user_id)
    access_token = create_access_token(data={"sub": str(token.user_id)})

    return TokenPair(access_token=access_token, refresh_token=new_refresh_token.token)


# Logout — révoque le refresh token
@auth_router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await revoke_refresh_token(db, request.refresh_token)
    return {"message": "Logged out successfully"}
