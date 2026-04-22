from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserLogin, UserRead
from app.core.security import get_password_hash
from app.crud.user import create_user as crud_create_user, get_user_by_email  # ← renommé
from app.core.security import verify_password, create_access_token
from app.dependencies import get_current_active_user

auth_router = APIRouter()

@auth_router.post("/create_user", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_active_user)):

    existing_user = await get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Address already registered"
        )
    hashed_password = get_password_hash(request.password)
    new_user = User(email=request.email, hashed_password=hashed_password)
    created_user = await crud_create_user(db, new_user)

    return created_user

@auth_router.post("/login")
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Vérification du mot de passe
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    # Génération du token d'accès
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")