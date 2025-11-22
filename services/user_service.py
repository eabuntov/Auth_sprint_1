from typing import Optional

from pydantic import EmailStr

from models.db_models import User
from repositories.user_repository import UserRepository
from security.password import PasswordHasher


class UserService:
    def __init__(self, repo: UserRepository, hasher: PasswordHasher):
        self.repo = repo
        self.hasher = hasher

    async def register(
        self,
        email: EmailStr,
        password: str,
        full_name: Optional[str] = None
    ):
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        password_hash = self.hasher.hash_password(password)

        return await self.repo.create(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
        )

    async def authenticate(self, email: EmailStr, password: str):
        user = await self.repo.get_by_email(email)
        if not user:
            return None

        if not self.hasher.verify_password(password, user.password_hash):
            return None

        return user

    async def change_password(self, user: User, old_password: str, new_password: str):
        if not self.hasher.verify_password(old_password, user.password_hash):
            raise ValueError("Old password incorrect")

        user.password_hash = self.hasher.hash_password(new_password)

        await self.repo.update(user)
        return user
