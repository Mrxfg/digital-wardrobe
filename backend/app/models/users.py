from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    telegram_id = Column(String, unique=True, nullable=False, index=True)

    username = Column(String, nullable=True)

    first_name = Column(String, nullable=True)

    avatar_url = Column(String, nullable=True)

    tier = Column(String, nullable=False, default="free")

    latitude = Column(Float, nullable=True)

    longitude = Column(Float, nullable=True)

    city = Column(String, nullable=True)

    timezone = Column(String, default="Europe/Moscow")

    notification_hour = Column(Integer, default=19)

    notification_minute = Column(Integer, default=0)

    notifications_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
