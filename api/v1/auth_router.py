from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import UUID

from dependencies import get_user_service, get_token_service, get_login_history_service, require_authenticated_user
from models.db_models import User
from models.models import UserRead, UserCreate, UserLogin, StandardResponse, LoginHistoryRead
from services.login_history_service import LoginHistoryService
from services.user_service import UserService
from services.token_service import TokenService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserRead)
async def register_user(
    data: UserCreate, users: UserService = Depends(get_user_service)
):
    return await users.register(
        email=data.email, password=data.password, full_name=data.full_name
    )


@auth_router.post("/login")
async def login_user(
    data: UserLogin,
    request: Request,
    users: UserService = Depends(get_user_service),
    tokens: TokenService = Depends(get_token_service),
    history: LoginHistoryService = Depends(get_login_history_service),
):
    user = await users.authenticate(data.email, data.password)

    # store login event
    await history.record_login(
        user.id,
        request.client.host,
        request.headers.get("User-Agent")
    )

    return tokens.create_token_pair(user)


@auth_router.post("/refresh")
async def refresh_token(
    refresh_token: str, tokens: TokenService = Depends(get_token_service)
):
    try:
        payload = tokens.decode_refresh(refresh_token)
        user_id = UUID(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    # Here you should fetch user and roles/entitlements from DB
    user = await get_user_service().repo.get_by_id(user_id)
    roles = [role.name for role in getattr(user, "roles", [])]
    entitlements = getattr(user, "entitlements", [])
    return tokens.create_token_pair(user, roles, entitlements)


@auth_router.post("/logout", response_model=StandardResponse)
async def logout(refresh_token: str, tokens: TokenService = Depends(get_token_service)):
    # Implement token revocation logic if needed
    return {"detail": "Logged out"}

@auth_router.get("/login-history", response_model=list[LoginHistoryRead])
async def get_login_history(
    current_user: User = Depends(require_authenticated_user),
    history: LoginHistoryService = Depends(get_login_history_service),
):
    return await history.get_user_history(current_user.id)