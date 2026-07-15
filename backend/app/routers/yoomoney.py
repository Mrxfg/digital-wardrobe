import hashlib
import logging
import os
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["YooMoney"])

PREMIUM_PRICE = 490  # RUB


def _verify_sha1(
    notification_type: str,
    operation_id: str,
    amount: str,
    currency: str,
    datetime: str,
    sender: str,
    codepro: str,
    label: str,
    received_hash: str,
    secret: str,
) -> bool:
    """Verify YooMoney notification signature.

    The hash is SHA1 of concatenated parameters separated by ``&``:
    ``notification_type&operation_id&amount&currency&datetime&sender&codepro&secret&label``
    """
    raw = f"{notification_type}&{operation_id}&{amount}&{currency}&{datetime}&{sender}&{codepro}&{secret}&{label}"
    expected = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return hmac.compare_digest(expected, received_hash)


@router.post("/yoomoney-webhook")
async def yoomoney_webhook(
    request: Request,
    notification_type: str = Form(...),
    operation_id: str = Form(...),
    amount: str = Form(...),
    currency: str = Form(...),
    datetime: str = Form(...),
    sender: str = Form(...),
    codepro: str = Form(...),
    label: str = Form(""),
    sha1_hash: str = Form(...),
    withdraw_amount: Optional[str] = Form(None),
    unaccepted: Optional[str] = Form(None),
):
    """Receive payment notifications from YooMoney.

    YooMoney sends HTTP POST with form-encoded data when a payment is made.
    See: https://yoomoney.ru/docs/payment/notifications
    """
    db: Session = next(get_db())

    try:
        logger.info(
            "YooMoney notification received: operation_id=%s, amount=%s, label=%s, sender=%s",
            operation_id,
            amount,
            label,
            sender,
        )

        # Verify secret exists
        secret = os.getenv("YOOMONEY_SECRET")
        if not secret:
            logger.error("YOOMONEY_SECRET environment variable is not set")
            raise HTTPException(status_code=500, detail="Webhook not configured")

        # Verify signature
        if not _verify_sha1(
            notification_type=notification_type,
            operation_id=operation_id,
            amount=amount,
            currency=currency,
            datetime=datetime,
            sender=sender,
            codepro=codepro,
            label=label,
            received_hash=sha1_hash,
            secret=secret,
        ):
            logger.warning("Invalid YooMoney signature for operation %s", operation_id)
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Check for pending (unaccepted) payments — skip them
        if unaccepted == "true":
            logger.info("Payment %s is not yet accepted, skipping", operation_id)
            return {"status": "pending"}

        # Check minimum amount (must be >= premium price)
        try:
            amount_float = float(amount)
            if amount_float < PREMIUM_PRICE:
                logger.warning(
                    "Payment %s amount %.2f is below premium price %d",
                    operation_id,
                    amount_float,
                    PREMIUM_PRICE,
                )
                return {"status": "accepted", "note": "amount below premium price"}
        except ValueError:
            logger.error("Invalid amount in notification: %s", amount)
            raise HTTPException(status_code=400, detail="Invalid amount")

        # Find user by label (telegram_id)
        if not label:
            logger.warning("Empty label in YooMoney notification %s", operation_id)
            return {"status": "accepted", "note": "no label"}

        user = db.query(User).filter(User.telegram_id == label).first()
        if not user:
            logger.warning("User with telegram_id=%s not found (operation %s)", label, operation_id)
            return {"status": "accepted", "note": "user not found"}

        # Upgrade user to premium
        old_tier = user.tier
        user.tier = "premium"
        db.commit()
        db.refresh(user)

        logger.info(
            "User %s upgraded from '%s' to '%s' via YooMoney payment (operation %s, amount %.2f RUB)",
            user.telegram_id,
            old_tier,
            user.tier,
            operation_id,
            amount_float,
        )

        return {"status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("YooMoney webhook error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()
