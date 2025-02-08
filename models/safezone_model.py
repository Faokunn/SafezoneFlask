from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class SafeZone(Base):
    __tablename__ = 'safe_zones'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_verified = Column(Boolean, default=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)
    name = Column(String(80), nullable=False)
    scale = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    time_of_day = Column(String(30), nullable=False)
    frequency = Column(String(30), nullable=False)
    status = Column(String, default="pending")
    report_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    user = relationship("User", back_populates="safe_zones")
    status_history = relationship("SafeZoneStatusHistory", back_populates="safe_zone", cascade="all, delete-orphan")

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
            "frequency": self.frequency,
            "report_timestamp": self.report_timestamp.isoformat() if self.report_timestamp else None
        }
