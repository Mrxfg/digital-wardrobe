from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    telegram_id = Column(String, unique=True, nullable=False, index=True)

    username = Column(String, nullable=True)

    first_name = Column(String, nullable=True)

    avatar_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
