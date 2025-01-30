from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class SafeZone(Base):
    __tablename__ = 'safe_zones'
    id = Column(Integer, primary_key=True)
    is_verified = Column(Boolean, default=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)
    name = Column(String(80), nullable=False)