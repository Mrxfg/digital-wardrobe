from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)

    outfit_id = Column(Integer, ForeignKey("outfits.id", ondelete="CASCADE"), nullable=False)

    clothing_id = Column(
        "clothing_item_id", Integer, ForeignKey("clothing_items.id", ondelete="CASCADE"), nullable=False
    )

    x = Column(Float, default=0.0)

    y = Column(Float, default=0.0)

    scale = Column(Float, default=1.0)

    outfit = relationship("Outfit", back_populates="items")

    clothing_item = relationship("ClothingItem")

    @property
    def image_url(self):
        return self.clothing_item.image_url if self.clothing_item else None
