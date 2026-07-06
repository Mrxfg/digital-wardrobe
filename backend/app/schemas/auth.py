from typing import Optional

from pydantic import BaseModel


class TelegramInitData(BaseModel):
    init_data: str


class LoginRequest(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    photo_url: Optional[str] = None


class RefreshRequest(BaseModel):
    access_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
