from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import UUID

from models.db_models import Subscription
from repositories.subscription_repository import SubscriptionRepository


class SubscriptionService:
    def __init__(self, repo: SubscriptionRepository):
        self.repo = repo

    async def add_subscription(
        self,
        user_id: UUID,
        name: str,
        entitlements: list[str],
        duration_days: Optional[int],
    ):
        now = datetime.now()
        ends = now + timedelta(days=duration_days) if duration_days else None
        return await self.repo.create(
            user_id=user_id,
            name=name,
            entitlements=",".join(entitlements),
            duration_days=duration_days,
            started_at=now,
            ends_at=ends,
        )

    async def extend(self, subscription: Subscription, extra_days: int):
        if subscription.ends_at:
            subscription.ends_at += timedelta(days=extra_days)
        else:
            subscription.ends_at = datetime.utcnow() + timedelta(days=extra_days)
        await self.repo.update(subscription)
        return subscription
