from typing import Optional

from pydantic import BaseModel

from app.schemas.outfit_item import OutfitItemCreate


class OutfitCreate(BaseModel):
    name: str


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    items: Optional[list[OutfitItemCreate]] = None


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str

    class Config:
        from_attributes = True
