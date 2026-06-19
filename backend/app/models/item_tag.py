from sqlalchemy import Column, ForeignKey, Integer

from app.database import Base


class ItemTag(Base):
    __tablename__ = "item_tags"

    id = Column(Integer, primary_key=True, index=True)

    clothing_item_id = Column(Integer, ForeignKey("clothing_items.id", ondelete="CASCADE"), nullable=False)

    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
