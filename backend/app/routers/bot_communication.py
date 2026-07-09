from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User

router = APIRouter(prefix="/bot-api", tags=["Bot Communication"])


class UserRegisterRequest(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None


class NotificationSettingsUpdate(BaseModel):
    notifications_enabled: bool
    notification_hour: Optional[int] = 19
    notification_minute: Optional[int] = 0


class UserForNotification(BaseModel):
    telegram_id: str
    first_name: Optional[str] = None
    notification_hour: int
    notification_minute: int


class UserSettingsResponse(BaseModel):
    notifications_enabled: bool
    notification_hour: int
    notification_minute: int


@router.get("/users/{telegram_id}/settings", response_model=UserSettingsResponse)
def get_user_settings(telegram_id: str, db: Session = Depends(get_db)):
    """Получить настройки уведомлений пользователя"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        return {
            "notifications_enabled": True,
            "notification_hour": 18,
            "notification_minute": 0,
        }

    return {
        "notifications_enabled": user.notifications_enabled or True,
        "notification_hour": user.notification_hour or 18,
        "notification_minute": user.notification_minute or 0,
    }


@router.post("/register-user")
def register_bot_user(data: UserRegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == data.telegram_id).first()

    if not user:
        user = User(
            telegram_id=data.telegram_id,
            username=data.username,
            first_name=data.first_name,
            notifications_enabled=True,
        )
        db.add(user)
    else:
        if user.notifications_enabled is None:
            user.notifications_enabled = True

    db.commit()
    return {"status": "success", "user_id": user.id}


@router.get("/users-to-notify", response_model=list[UserForNotification])
def get_users_to_notify(hour: int, minute: int = 0, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(
            User.notifications_enabled.is_(True),
            User.notification_hour == hour,
            User.notification_minute == minute,
        )
        .all()
    )

    return [
        {
            "telegram_id": u.telegram_id,
            "first_name": u.first_name,
            "notification_hour": u.notification_hour,
            "notification_minute": u.notification_minute,
        }
        for u in users
    ]


@router.patch("/users/{telegram_id}/settings")
def update_user_settings(
    telegram_id: str,
    settings: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.notifications_enabled = settings.notifications_enabled
    if settings.notification_hour is not None:
        user.notification_hour = settings.notification_hour
    if settings.notification_minute is not None:
        user.notification_minute = settings.notification_minute
    db.commit()
    return {"status": "success"}
