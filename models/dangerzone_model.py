from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class DangerZone(Base):
    __tablename__ = 'danger_zones'
    id = Column(Integer, primary_key=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)
    name = Column(String(80), nullable=False)

    incident_reports = relationship("IncidentReport", back_populates="danger_zone", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "is_verified": self.is_verified,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "name": self.name,
        }
