from datetime import date
from typing import Optional

from pydantic import BaseModel


class WearRecordCreate(BaseModel):
    outfit_id: int
    worn_date: date


class WearRecordUpdate(BaseModel):
    outfit_id: Optional[int] = None
    worn_date: Optional[date] = None


class WearRecordOutfitItem(BaseModel):
    clothing_id: int
    image_url: Optional[str] = None


class WearRecordOutfit(BaseModel):
    name: str
    items: list[WearRecordOutfitItem] = []


class WearRecordResponse(BaseModel):
    id: int
    user_id: int
    outfit_id: int
    worn_date: date
    outfit: Optional[WearRecordOutfit] = None

    class Config:
        from_attributes = True
