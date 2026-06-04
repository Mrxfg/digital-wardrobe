from pydantic import BaseModel


class ClothingItemCreate(BaseModel):
    name: str
    category: str
    season: str
    image_url: str | None = None


class ClothingItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    season: str | None = None
    image_url: str | None = None


class ClothingItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: str
    season: str
    image_url: str | None = None

    class Config:
        from_attributes = True