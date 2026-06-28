from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)

    outfit_id = Column(Integer, ForeignKey("outfits.id", ondelete="CASCADE"), nullable=False)

    clothing_item_id = Column(Integer, ForeignKey("clothing_items.id", ondelete="CASCADE"), nullable=False)

    position = Column(String, nullable=False, default="other")
