from pydantic import BaseModel


class TierLimits(BaseModel):
    max_items: int
    max_outfits: int
    max_capsules: int
    ai_stylist: bool


class SubscriptionStatus(BaseModel):
    tier: str
    items_count: int
    outfits_count: int
    capsules_count: int
    limits: TierLimits


class SetPremiumRequest(BaseModel):
    telegram_id: str


class SetPremiumResponse(BaseModel):
    telegram_id: str
    tier: str
    message: str
