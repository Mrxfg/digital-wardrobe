from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class CapsuleItem(Base):
    __tablename__ = "capsule_items"

    id = Column(Integer, primary_key=True, index=True)

    capsule_id = Column(Integer, ForeignKey("capsules.id", ondelete="CASCADE"), nullable=False)

    clothing_item_id = Column(Integer, ForeignKey("clothing_items.id", ondelete="CASCADE"), nullable=False)

    clothing_item = relationship("ClothingItem")

    @property
    def image_url(self):
        return self.clothing_item.image_url if self.clothing_item else None
