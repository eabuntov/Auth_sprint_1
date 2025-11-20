from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, UUID

from models.db_models import Role


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, role_id: UUID):
        result = await self.session.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()


    async def get_by_name(self, name: str):
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()


    async def create(self, **kwargs):
        role = Role(**kwargs)
        self.session.add(role)
        await self.session.flush()
        return role


    async def update(self, role: Role, **kwargs):
        for k, v in kwargs.items():
            setattr(role, k, v)
        await self.session.flush()
        return role


    async def delete(self, role: Role):
        await self.session.delete(role)