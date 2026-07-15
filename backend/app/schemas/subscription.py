from enum import Enum

from pydantic import BaseModel


class TierEnum(str, Enum):
    free = "free"
    premium = "premium"


class TierLimits(BaseModel):
    max_items: int
    max_outfits: int
    max_capsules: int
    ai_stylist: bool


class SubscriptionStatus(BaseModel):
    tier: TierEnum
    items_count: int
    outfits_count: int
    capsules_count: int
    limits: TierLimits


class SetUserTierRequest(BaseModel):
    telegram_id: str


class SetUserTierResponse(BaseModel):
    telegram_id: str
    tier: TierEnum
    message: str
