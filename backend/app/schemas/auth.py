from pydantic import BaseModel


class TelegramLogin(BaseModel):
    telegram_id: str
    username: str | None = None
    first_name: str | None = None
    avatar_url: str | None = None


class TelegramInitData(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
