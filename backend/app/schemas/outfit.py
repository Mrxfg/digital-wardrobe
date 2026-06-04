from pydantic import BaseModel


class OutfitCreate(BaseModel):
    name: str


class OutfitUpdate(BaseModel):
    name: str | None = None


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str

    class Config:
        from_attributes = True