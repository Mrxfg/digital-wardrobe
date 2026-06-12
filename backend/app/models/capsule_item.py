from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class CapsuleItem(Base):
    __tablename__ = "capsule_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    capsule_id = Column(
        Integer,
        ForeignKey("capsules.id"),
        nullable=False
    )

    clothing_item_id = Column(
        Integer,
        ForeignKey("clothing_items.id"),
        nullable=False
    )