from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TagWithCount(TagResponse):
    item_count: int
