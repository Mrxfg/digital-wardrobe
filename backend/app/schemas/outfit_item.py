from pydantic import BaseModel


class OutfitItemCreate(BaseModel):
    clothing_item_id: int


class OutfitItemResponse(BaseModel):
    id: int
    outfit_id: int
    clothing_item_id: int

    class Config:
        from_attributes = True