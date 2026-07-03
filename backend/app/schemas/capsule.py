from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CapsuleCreate(BaseModel):
    name: str
    items: list[int] = []


class CapsuleUpdate(BaseModel):
    name: str | None = None


class CapsuleItemLight(BaseModel):
    id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class CapsuleListResponse(BaseModel):
    id: int
    user_id: int
    name: str
    is_deleted: bool = False
    items: list[CapsuleItemLight] = []

    class Config:
        from_attributes = True


class CapsuleOutfitItem(BaseModel):
    clothing_id: int
    image_url: Optional[str] = None
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0


class CapsuleOutfit(BaseModel):
    name: str
    items: list[CapsuleOutfitItem] = []


class CapsuleDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    items: list[CapsuleItemLight] = []
    outfits: list[CapsuleOutfit] = []

    class Config:
        from_attributes = True


class CapsuleResponse(BaseModel):
    id: int
    user_id: int
    name: str
    is_deleted: bool = False
    days_until_deleted: int | None = None
    items: list[CapsuleItemLight] = []

    class Config:
        from_attributes = True
