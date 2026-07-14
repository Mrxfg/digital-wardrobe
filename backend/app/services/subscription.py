import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.capsule import Capsule
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit

logger = logging.getLogger(__name__)

FREE_TIER_LIMITS = {
    "items": 10,
    "outfits": 3,
    "capsules": 1,
}

PREMIUM_TIER_LIMITS = {
    "items": 9999,
    "outfits": 9999,
    "capsules": 9999,
}

TIER_LIMITS = {
    "free": FREE_TIER_LIMITS,
    "premium": PREMIUM_TIER_LIMITS,
}


def check_free_tier_limit(
    db: Session,
    user_id: int,
    tier: str,
    resource: str,
) -> None:
    """Check if a free-tier user has reached their limit for a given resource.

    Returns 403 with ``limit_reached`` error if the limit is exceeded.
    Raises 403 for unknown resource names.

    Supported resources: items, outfits, capsules.
    """
    if tier != "free":
        return

    limits = TIER_LIMITS.get(tier)
    if limits is None:
        raise HTTPException(
            status_code=403,
            detail={"error": "unknown_tier", "message": f"Unknown tier: {tier}"},
        )

    max_count = limits.get(resource)
    if max_count is None:
        raise HTTPException(
            status_code=403,
            detail={"error": "limit_reached", "message": f"Unknown resource: {resource}"},
        )

    models_map = {
        "items": ClothingItem,
        "outfits": Outfit,
        "capsules": Capsule,
    }

    model_class = models_map.get(resource)
    count = (
        db.query(model_class)
        .filter(
            model_class.user_id == user_id,
            model_class.is_deleted.is_(False),
        )
        .count()
    )

    if count >= max_count:
        resource_labels = {
            "items": "clothing items",
            "outfits": "outfits",
            "capsules": "capsules",
        }
        label = resource_labels.get(resource, resource)
        raise HTTPException(
            status_code=403,
            detail={
                "error": "limit_reached",
                "message": f"Free tier allows max {max_count} {label}",
            },
        )


def require_premium(tier: str) -> None:
    """Require premium tier for AI Stylist access.

    Returns 403 with ``premium_required`` error for free-tier users.
    """
    if tier != "premium":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "AI Stylist requires Premium subscription",
            },
        )
