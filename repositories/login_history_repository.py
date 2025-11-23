from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.db_models import LoginHistory

class LoginHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id, ip_address, user_agent):
        record = LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_by_user(self, user_id):
        result = await self.session.execute(
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.timestamp.desc())
        )
        return result.scalars().all()
