from typing import Optional

from pydantic import BaseModel


class OutfitItemCreate(BaseModel):
    clothing_item_id: int
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0


class OutfitItemResponse(BaseModel):
    id: int
    outfit_id: int
    clothing_item_id: int
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
