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
    scale = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    time_of_day = Column(String(30), nullable=False)
    frequency = Column(String(30), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "is_verified": self.is_verified,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "name": self.name,
            "scale": self.scale,
            "description": self.description,
            "time_of_day": self.time_of_day,
            "frequency": self.frequency
        }
