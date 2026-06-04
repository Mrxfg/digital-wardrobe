from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    telegram_id: str
    username: str | None = None

    class Config:
        from_attributes = True