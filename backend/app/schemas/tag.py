from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True
