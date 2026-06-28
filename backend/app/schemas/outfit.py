from datetime import datetime

from pydantic import BaseModel

from app.schemas.clothing_item import ClothingItemResponse


class OutfitItemCreate(BaseModel):
    clothing_item_id: int
    position: str = "other"


class OutfitItemResponse(BaseModel):
    id: int
    outfit_id: int
    clothing_item_id: int
    position: str

    class Config:
        from_attributes = True


class OutfitCreate(BaseModel):
    name: str
    top: int | None = None
    bottom: int | None = None
    shoes: int | None = None
    accessory: int | None = None


class OutfitUpdate(BaseModel):
    name: str | None = None
    top: int | None = None
    bottom: int | None = None
    shoes: int | None = None
    accessory: int | None = None


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    is_deleted: bool = False
    created_at: datetime | None = None
    top: ClothingItemResponse | None = None
    bottom: ClothingItemResponse | None = None
    shoes: ClothingItemResponse | None = None
    accessory: ClothingItemResponse | None = None

    class Config:
        from_attributes = True
