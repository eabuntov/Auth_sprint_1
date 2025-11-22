from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_subscription_service
from models.models import SubscriptionAssign, SubscriptionRead
from services.subscription_service import SubscriptionService

subscriptions_router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@subscriptions_router.post("/assign", response_model=SubscriptionRead)
async def assign_subscription(
    data: SubscriptionAssign,
    subs: SubscriptionService = Depends(get_subscription_service),
):
    try:
        subscription = await subs.assign(
            user_id=data.user_id, subscription_type=data.subscription_type
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return subscription


@subscriptions_router.delete("/revoke/{sub_id}")
async def revoke_subscription(
    sub_id: int, subs: SubscriptionService = Depends(get_subscription_service)
):
    try:
        await subs.revoke(sub_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"detail": "Subscription revoked"}
