from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Capsule(Base):
    __tablename__ = "capsules"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)

    description = Column(String, nullable=True)

    season = Column(String, nullable=True)

    user = relationship("User")

    capsule_items = relationship("CapsuleItem", backref="capsule_rel", cascade="all, delete-orphan")

    items = relationship("ClothingItem", secondary="capsule_items", viewonly=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
