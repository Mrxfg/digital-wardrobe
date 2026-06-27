from pydantic import BaseModel

from app.schemas.clothing_item import ClothingItemResponse


class OutfitCreate(BaseModel):
    name: str


class OutfitUpdate(BaseModel):
    name: str | None = None


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    is_deleted: bool = False
    items: list[ClothingItemResponse] = []

    class Config:
        from_attributes = True
