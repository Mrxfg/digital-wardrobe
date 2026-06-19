from datetime import datetime

from pydantic import BaseModel


class ClothingItemCreate(BaseModel):
    name: str
    category: str
    color: str
    season: str
    material: str
    image_url: str | None = None
    original_image_url: str | None = None


class ClothingItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    color: str | None = None
    season: str | None = None
    material: str | None = None
    image_url: str | None = None
    original_image_url: str | None = None


class ClothingItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: str
    color: str
    season: str
    material: str
    image_url: str | None = None
    original_image_url: str | None = None
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True
