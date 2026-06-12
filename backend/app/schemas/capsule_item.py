from pydantic import BaseModel


class CapsuleItemCreate(BaseModel):
    clothing_item_id: int


class CapsuleItemResponse(BaseModel):
    id: int
    capsule_id: int
    clothing_item_id: int

    class Config:
        from_attributes = True