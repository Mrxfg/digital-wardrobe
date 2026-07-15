import hashlib
import hmac
import logging
import os

from fastapi import APIRouter, HTTPException, Request
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
):
    """Receive payment notifications from YooMoney.

    YooMoney sends HTTP POST with form-encoded data when a payment is made.
    See: https://yoomoney.ru/docs/payment/notifications
    """
    db: Session = next(get_db())

    try:
        # Parse form data manually (YooMoney may send extra fields)
        form = await request.form()
        form_data = {k: v for k, v in form.items()}

        notification_type = form_data.get("notification_type", "")
        operation_id = form_data.get("operation_id", "")
        amount = form_data.get("amount", "0")
        currency = form_data.get("currency", "")
        datetime_str = form_data.get("datetime", "")
        sender = form_data.get("sender", "")
        codepro = form_data.get("codepro", "false")
        label = form_data.get("label", "")
        sha1_hash = form_data.get("sha1_hash", "")
        unaccepted = form_data.get("unaccepted")

        logger.info(
            "YooMoney notification received: operation_id=%s, amount=%s, label=%s, sender=%s, all_fields=%s",
            operation_id,
            amount,
            label,
            sender,
            list(form_data.keys()),
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
            datetime=datetime_str,
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
