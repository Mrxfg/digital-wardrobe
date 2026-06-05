from datetime import date
from pydantic import BaseModel


class WearRecordCreate(BaseModel):
    outfit_id: int
    worn_date: date


class WearRecordResponse(BaseModel):
    id: int
    user_id: int
    outfit_id: int
    worn_date: date

    class Config:
        from_attributes = True