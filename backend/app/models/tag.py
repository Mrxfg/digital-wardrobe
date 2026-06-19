from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clothing_items = relationship("ClothingItem", secondary="item_tags", back_populates="tags")
