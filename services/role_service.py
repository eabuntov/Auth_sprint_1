from typing import Optional

from models.db_models import User, Role
from repositories.roles_repository import RoleRepository


class RoleService:
    def __init__(self, repo: RoleRepository):
        self.repo = repo

    async def create_role(
        self, name: str, permissions: str, description: Optional[str] = None
    ):
        role = await self.repo.get_by_name(name)
        if role:
            raise ValueError("Role already exists")
        return await self.repo.create(
            name=name, permissions=permissions, description=description
        )

    async def assign_role(self, user: User, role: Role):
        if role not in user.roles:
            user.roles.append(role)
        return user
