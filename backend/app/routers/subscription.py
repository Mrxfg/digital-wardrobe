import hashlib
import hmac
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.capsule import Capsule
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.users import User
from app.schemas.subscription import SetUserTierRequest, SetUserTierResponse, SubscriptionStatus, TierLimits
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
        tier=tier,
        items_count=items_count,
        outfits_count=outfits_count,
        capsules_count=capsules_count,
        limits=limits,
    )


@router.post("/set-tier", response_model=SetUserTierResponse)
def set_user_tier(
    body: SetUserTierRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually set a user's tier (admin endpoint). Valid tiers: free, premium."""
    tier = body.tier.lower()
    if tier not in ("free", "premium"):
        raise HTTPException(status_code=400, detail="Invalid tier. Use 'free' or 'premium'")

    user = db.query(User).filter(User.telegram_id == body.telegram_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_tier = user.tier
    user.tier = tier
    db.commit()
    db.refresh(user)

    action = "upgraded" if tier == "premium" else "downgraded"
    message = f"User {user.telegram_id} {action} from '{old_tier}' to '{tier}'"

    return SetUserTierResponse(
        telegram_id=user.telegram_id,
        tier=user.tier,
        message=message,
    )
