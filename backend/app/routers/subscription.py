import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.capsule import Capsule
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.users import User
from app.schemas.subscription import (
    CreatePaymentResponse,
    PaymentType,
    SetUserTierRequest,
    SetUserTierResponse,
    SubscriptionStatus,
    TierEnum,
    TierLimits,
)
from app.services.subscription import FREE_TIER_LIMITS, PREMIUM_TIER_LIMITS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscription", tags=["Subscription"])

# Price for premium in RUB
PREMIUM_PRICE = 490


@router.get("/status", response_model=SubscriptionStatus)
def get_subscription_status(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's subscription status and resource usage."""
    user_id = current_user["user_id"]

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tier = user.tier or "free"

    items_count = (
        db.query(ClothingItem)
        .filter(
            ClothingItem.user_id == user_id,
            ClothingItem.is_deleted.is_(False),
        )
        .count()
    )

    outfits_count = (
        db.query(Outfit)
        .filter(
            Outfit.user_id == user_id,
            Outfit.is_deleted.is_(False),
        )
        .count()
    )

    capsules_count = (
        db.query(Capsule)
        .filter(
            Capsule.user_id == user_id,
            Capsule.is_deleted.is_(False),
        )
        .count()
    )

    limits_map = {
        "free": FREE_TIER_LIMITS,
        "premium": PREMIUM_TIER_LIMITS,
    }
    limits_data = limits_map.get(tier, FREE_TIER_LIMITS)

    limits = TierLimits(
        max_items=limits_data["items"],
        max_outfits=limits_data["outfits"],
        max_capsules=limits_data["capsules"],
        ai_stylist=(tier == "premium"),
    )

    return SubscriptionStatus(
        tier=TierEnum(tier),
        items_count=items_count,
        outfits_count=outfits_count,
        capsules_count=capsules_count,
        limits=limits,
    )


@router.post("/set-tier/{tier}", response_model=SetUserTierResponse)
def set_user_tier(
    tier: TierEnum,
    body: SetUserTierRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually set a user's tier (admin endpoint)."""
    user = db.query(User).filter(User.telegram_id == body.telegram_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_tier = user.tier
    tier_value = tier.value
    user.tier = tier_value
    db.commit()
    db.refresh(user)

    action = "upgraded" if tier_value == "premium" else "downgraded"
    message = f"User {user.telegram_id} {action} from '{old_tier}' to '{tier_value}'"

    return SetUserTierResponse(
        telegram_id=user.telegram_id,
        tier=user.tier,
        message=message,
    )


@router.post("/create-payment/{payment_type}", response_model=CreatePaymentResponse)
def create_payment(
    payment_type: PaymentType,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a YooMoney payment URL for premium subscription.

    Returns a URL the user should open to complete payment.
    After successful payment, YooMoney sends a webhook to /yoomoney-webhook.
    """
    user_id = current_user["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    receiver = os.getenv("YOOMONEY_RECEIVER")
    if not receiver:
        raise HTTPException(status_code=500, detail="YOOMONEY_RECEIVER not configured")

    description = "Digital Wardrobe Premium"

    # Build YooMoney quickpay form URL
    params = {
        "receiver": receiver,
        "quickpay-form": "shop",
        "targets": description,
        "paymentType": payment_type.value,
        "sum": str(PREMIUM_PRICE),
        "label": user.telegram_id,
    }
    from urllib.parse import urlencode

    payment_url = f"https://yoomoney.ru/quickpay/confirm.xml?{urlencode(params)}"

    return CreatePaymentResponse(
        payment_url=payment_url,
        amount=PREMIUM_PRICE,
        label=user.telegram_id,
        description=description,
    )
