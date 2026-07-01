from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CapsuleCreate(BaseModel):
    name: str
    description: str | None = None
    season: str | None = None
    items: list[int] = []


class CapsuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    season: str | None = None


class CapsuleItemLight(BaseModel):
    id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class CapsuleListResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    season: Optional[str] = None
    is_deleted: bool = False
    items: list[CapsuleItemLight] = []

    class Config:
        from_attributes = True


class CapsuleOutfitItem(BaseModel):
    clothing_id: int
    image_url: Optional[str] = None


class CapsuleOutfit(BaseModel):
    name: str
    items: list[CapsuleOutfitItem] = []


class CapsuleDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    season: Optional[str] = None
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    items: list[int] = []
    outfits: list[CapsuleOutfit] = []

    class Config:
        from_attributes = True


class CapsuleResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None = None
    season: str | None = None
    is_deleted: bool = False
    items: list[CapsuleItemLight] = []

    class Config:
        from_attributes = True
