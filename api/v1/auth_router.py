from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_user_service, get_token_service
from models.models import UserRead, UserCreate, UserLogin
from services.user_service import UserService
from services.token_service import TokenService

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserRead)
async def register_user(data: UserCreate, users: UserService = Depends(get_user_service)):
    return await users.register(email=data.email, password=data.password, full_name=data.full_name)

@auth_router.post("/login")
async def login_user(data: UserLogin, users: UserService = Depends(get_user_service), tokens: TokenService = Depends(get_token_service)):
    user = await users.authenticate(data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # For roles and entitlements, fetch them from user object or service
    roles = [role.name for role in getattr(user, 'roles', [])]
    entitlements = getattr(user, 'entitlements', [])
    return tokens.create_token_pair(user, roles, entitlements)

@auth_router.post("/refresh")
async def refresh_token(refresh_token: str, tokens: TokenService = Depends(get_token_service)):
    try:
        payload = tokens.decode_refresh(refresh_token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    # Here you should fetch user and roles/entitlements from DB
    user = await get_user_service().repo.get_by_id(user_id)
    roles = [role.name for role in getattr(user, 'roles', [])]
    entitlements = getattr(user, 'entitlements', [])
    return tokens.create_token_pair(user, roles, entitlements)

@auth_router.post("/logout")
async def logout(refresh_token: str, tokens: TokenService = Depends(get_token_service)):
    # Implement token revocation logic if needed
    return {"detail": "Logged out"}