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


class PaymentType(str, Enum):
    bank_card = "AC"        # Банковская карта
    yoomoney_wallet = "PC"  # Кошелёк YooMoney
    phone_balance = "MC"    # Баланс телефона
    cash = "GP"             # Наличные через терминалы
    sberbank = "SB"         # Сбербанк Онлайн
    alfa_click = "AB"       # Альфа-Клик


class CreatePaymentRequest(BaseModel):
    payment_type: PaymentType = PaymentType.bank_card


class CreatePaymentResponse(BaseModel):
    payment_url: str
    amount: int
    label: str
    description: str
