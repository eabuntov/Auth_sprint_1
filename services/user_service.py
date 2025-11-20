import bcrypt
from typing import Optional

from models.db_models import User
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register(
        self, email: str, password: str, full_name: Optional[str] = None
    ):
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return await self.repo.create(
            email=email, full_name=full_name, password_hash=password_hash
        )

    async def authenticate(self, email: str, password: str):
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return None
        return user

    async def change_password(self, user: User, old_password: str, new_password: str):
        if not bcrypt.checkpw(old_password.encode(), user.password_hash.encode()):
            raise ValueError("Old password incorrect")
        user.password_hash = bcrypt.hashpw(
            new_password.encode(), bcrypt.gensalt()
        ).decode()
        await self.repo.update(user)
        return user
