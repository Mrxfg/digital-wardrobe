from typing import Optional

from pydantic import BaseModel

from app.schemas.outfit_item import OutfitItemCreate


class OutfitCreate(BaseModel):
    name: str
    items: list[OutfitItemCreate] = []


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    items: Optional[list[OutfitItemCreate]] = None


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    capsule_id: int | None = None
    is_deleted: bool = False
    days_until_deleted: int | None = None

    class Config:
        from_attributes = True
