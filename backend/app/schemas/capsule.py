from datetime import datetime

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


class CapsuleItemLightResponse(BaseModel):
    """Lightweight item response — only id + image_url for performance."""
    id: int
    image_url: str | None = None

    class Config:
        from_attributes = True


class CapsuleResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None = None
    season: str | None = None
    is_deleted: bool = False
    created_at: datetime | None = None
    items: list[CapsuleItemLightResponse] = []

    class Config:
        from_attributes = True


class CapsuleOutfitItemResponse(BaseModel):
    """Item inside an outfit within a capsule detail."""
    clothing_id: int
    x: float
    y: float
    scale: float


class CapsuleOutfitResponse(BaseModel):
    """Outfit inside a capsule detail."""
    name: str
    items: list[CapsuleOutfitItemResponse] = []


class CapsuleDetailResponse(BaseModel):
    """Full capsule detail with items (as IDs) and outfits."""
    id: int
    user_id: int
    name: str
    description: str | None = None
    season: str | None = None
    is_deleted: bool = False
    created_at: datetime | None = None
    items: list[int] = []
    outfits: list[CapsuleOutfitResponse] = []

    class Config:
        from_attributes = True
