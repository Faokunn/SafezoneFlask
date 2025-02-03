from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Time, JSON, Date, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP
from datetime import datetime, timezone
from database.base import Base

class SafeZoneStatusHistory(Base):
    __tablename__ = 'safe_zone_status_history'
    id = Column(Integer, primary_key=True)
    safe_zone_id = Column(Integer, ForeignKey('safe_zones.id'), nullable=False)
    status = Column(String, nullable=False)  
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))  
    remarks = Column(Text, nullable=True)  

    safe_zone = relationship("SafeZone", back_populates="status_history")