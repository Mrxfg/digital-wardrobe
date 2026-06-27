from pydantic import BaseModel

from app.schemas.clothing_item import ClothingItemResponse


class CapsuleCreate(BaseModel):
    name: str
    description: str | None = None
    season: str | None = None
    items: list[int] = []


class CapsuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    season: str | None = None


class CapsuleResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None = None
    season: str | None = None
    items: list[ClothingItemResponse] = []

    class Config:
        from_attributes = True
