from datetime import datetime

from pydantic import BaseModel

from app.schemas.outfit_item import OutfitItemCreate, OutfitItemWithClothingResponse


class OutfitCreate(BaseModel):
    name: str
    items: list[OutfitItemCreate] = []


class OutfitUpdate(BaseModel):
    name: str | None = None
    items: list[OutfitItemCreate] | None = None


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    is_deleted: bool = False
    created_at: datetime | None = None
    items: list[OutfitItemWithClothingResponse] = []

    class Config:
        from_attributes = True
