import hashlib
import hmac
import json
import os
from typing import Optional
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.schemas.auth import LoginRequest, RefreshRequest, TelegramInitData, TokenResponse
from app.services.auth import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

BOT_TOKEN = os.getenv("BOT_TOKEN")


def verify_telegram_webapp_data(init_data: str) -> Optional[dict]:
    """
    Verify Telegram WebApp initData signature.
    Returns parsed user data if valid, None if invalid.
    """
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")

    try:
        # Parse init_data
        parsed_data = dict(parse_qsl(init_data))

        if "hash" not in parsed_data:
            return None

        received_hash = parsed_data.pop("hash")

        # Create data check string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = "\n".join(data_check_arr)

        # Calculate secret key
        secret_key = hmac.new(key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256).digest()

        # Calculate hash
        calculated_hash = hmac.new(key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

        # Verify hash
        if calculated_hash != received_hash:
            return None

        # Parse user data
        if "user" in parsed_data:
            user_data = json.loads(parsed_data["user"])
            return user_data

        return None

    except Exception as e:
        print(f"Error verifying Telegram data: {e}")
        return None


@router.post("/telegram-webapp", response_model=TokenResponse)
def telegram_webapp_login(payload: TelegramInitData, db: Session = Depends(get_db)):
    """
    Authenticate user via Telegram Mini App.
    Verifies initData signature from Telegram WebApp.

    This is the SECURE endpoint that should be used in production.
    """
    # Verify Telegram signature
    user_data = verify_telegram_webapp_data(payload.init_data)

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication data")

    telegram_id = str(user_data.get("id"))
    username = user_data.get("username")
    first_name = user_data.get("first_name")
    photo_url = user_data.get("photo_url")

    # Find or create user
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            avatar_url=photo_url,
        )
        db.add(user)
    else:
        # Update existing user
        user.username = username
        user.first_name = first_name
        user.avatar_url = photo_url

    db.commit()
    db.refresh(user)

    # Create JWT token
    token = create_access_token(user.id)

    return {"access_token": token, "token_type": "bearer"}  # nosec B105


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Simple login by telegram_id. Returns a JWT token for the user."""
    user = db.query(User).filter(User.telegram_id == payload.telegram_id).first()

    if not user:
        user = User(
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            avatar_url=payload.photo_url,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)

    return {"access_token": token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    """Refresh an expired token. Returns a new JWT if current token is valid."""
    payload_data = decode_access_token(payload.access_token)

    if not payload_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload_data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    token = create_access_token(user_id)

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    return user
