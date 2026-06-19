from pydantic import BaseModel


class TelegramInitData(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
