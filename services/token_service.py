from datetime import datetime, timedelta

from jose import jwt, JWTError

from models.db_models import User
from services.settings import settings


class TokenService:
    def create_access_token(
        self, user: User, roles: list[str], entitlements: list[str]
    ):
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "roles": roles,
            "entitlements": entitlements,
            "exp": expire,
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)
        return token

    def create_refresh_token(self, user: User):
        expire = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": expire,
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)
        return token

    def decode(self, token: str):
        try:
            return jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO]
            )
        except JWTError:
            return None
