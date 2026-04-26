from fastapi import APIRouter
from app.api.v1.endpoints.auth import auth_router
from app.api.v1.endpoints.department import department_router
from app.api.v1.endpoints.user import user_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(department_router, prefix="/departments", tags=["Department"])
api_router.include_router(user_router, prefix="/users", tags=["User"])
