from pydantic import BaseModel


class CapsuleCreate(BaseModel):
    name: str
    season: str | None = None


class CapsuleUpdate(BaseModel):
    name: str | None = None
    season: str | None = None


class CapsuleResponse(BaseModel):
    id: int
    user_id: int
    name: str
    season: str | None = None

    class Config:
        from_attributes = True
