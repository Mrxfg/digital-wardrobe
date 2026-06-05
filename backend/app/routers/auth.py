from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.dependencies.auth import get_current_user

from app.schemas.auth import (
    TelegramLogin,
    TokenResponse
)

from app.services.auth import (
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/telegram",
    response_model=TokenResponse
)
def telegram_login(
    payload: TelegramLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.telegram_id == payload.telegram_id
    ).first()

    if not user:
        user = User(
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            avatar_url=payload.avatar_url
        )

        db.add(user)

    else:
        user.username = payload.username
        user.first_name = payload.first_name
        user.avatar_url = payload.avatar_url

    db.commit()
    db.refresh(user)

    token = create_access_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
@router.get("/me")
def get_me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == current_user["user_id"]
    ).first()

    return user