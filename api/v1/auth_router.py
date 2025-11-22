from fastapi import APIRouter, Depends

from dependencies import get_user_service, get_token_service
from models.models import UserRead, UserCreate
from services.token_service import TokenService
from services.user_service import UserService

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserRead)
async def register_user(data: UserCreate, users: UserService = Depends(get_user_service)):
    return await users.register(data)

@auth_router.post("/login")
async def login_user(data: UserLogin, users: UserService = Depends(get_user_service), tokens: TokenService = Depends(get_token_service)):
    user = await users.authenticate(data.email, data.password)
    return await tokens.create_token_pair(user)

@auth_router.post("/refresh")
async def refresh_token(refresh_token: str, tokens: TokenService = Depends(get_token_service)):
    return await tokens.refresh(refresh_token)

@auth_router.post("/logout")
async def logout(refresh_token: str, tokens: TokenService = Depends(get_token_service)):
    await tokens.revoke(refresh_token)
    return {"detail": "Logged out"}