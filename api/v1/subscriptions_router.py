from fastapi import APIRouter, Depends

from dependencies import get_subscription_service
from models.db_models import SubscriptionAssign
from models.models import SubscriptionRead
from services.subscription_service import SubscriptionService

subscriptions_router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@subscriptions_router.post("/assign", response_model=SubscriptionRead)
async def assign_subscription(data: SubscriptionAssign, subs: SubscriptionService = Depends(get_subscription_service)):
    return await subs.assign(data.user_id, data.subscription_type)

@subscriptions_router.delete("/revoke/{sub_id}")
async def revoke_subscription(sub_id: int, subs: SubscriptionService = Depends(get_subscription_service)):
    await subs.revoke(sub_id)
    return {"detail": "Subscription revoked"}