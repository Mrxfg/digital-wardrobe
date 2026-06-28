from pydantic import BaseModel


class OutfitItemCreate(BaseModel):
    clothing_id: int
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0


class OutfitItemResponse(BaseModel):
    id: int
    outfit_id: int
    clothing_id: int
    x: float
    y: float
    scale: float

    class Config:
        from_attributes = True


class OutfitItemWithClothingResponse(BaseModel):
    id: int
    outfit_id: int
    clothing_id: int
    x: float
    y: float
    scale: float
    image_url: str | None = None

    class Config:
        from_attributes = True
