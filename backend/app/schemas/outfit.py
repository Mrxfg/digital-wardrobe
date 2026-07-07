from typing import Optional, Union

from pydantic import BaseModel, field_validator

from app.schemas.outfit_item import OutfitItemCreate, OutfitItemResponse


class OutfitCreate(BaseModel):
    name: str
    capsule_id: Optional[int] = None
    items: list[Union[int, OutfitItemCreate]] = []

    @field_validator("items", mode="before")
    @classmethod
    def coerce_items(cls, v):
        if not isinstance(v, list):
            return v
        return [{"clothing_item_id": item} if isinstance(item, (int, float)) else item for item in v]


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    capsule_id: Optional[int] = None
    items: Optional[list[Union[int, OutfitItemCreate]]] = None

    @field_validator("items", mode="before")
    @classmethod
    def coerce_items(cls, v):
        if not isinstance(v, list):
            return v
        return [{"clothing_item_id": item} if isinstance(item, (int, float)) else item for item in v]


class GenerateOutfitRequest(BaseModel):
    capsule_id: Optional[int] = None


class GenerateOutfitItem(BaseModel):
    clothing_item_id: int
    name: str
    image_url: Optional[str] = None
    category: str
    color: str


class GenerateOutfitSuggestion(BaseModel):
    name: str
    items: list[GenerateOutfitItem]


class GenerateOutfitResponse(BaseModel):
    suggestions: list[GenerateOutfitSuggestion]
    fallback: bool = False


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    capsule_id: int | None = None
    is_deleted: bool = False
    days_until_deleted: int | None = None
    items: list[OutfitItemResponse] = []

    class Config:
        from_attributes = True
