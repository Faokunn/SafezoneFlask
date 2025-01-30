from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Time, JSON, Date, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pytz
from database.base import Base

class IncidentReport(Base):
    __tablename__ = 'incident_reports'
    id = Column(Integer, primary_key=True)
    danger_zone_id = Column(Integer, ForeignKey('danger_zones.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    description = Column(Text, nullable=False)
    report_date = Column(Date, nullable=False)
    report_time = Column(Time, nullable=False)
    images = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    report_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

    danger_zone = relationship("DangerZone", back_populates="incident_reports")
    user = relationship("User", back_populates="incident_reports")
    status_history = relationship("IncidentReportStatusHistory", back_populates="incident_report", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "danger_zone_id": self.danger_zone_id,
            "description": self.description,
            "report_date": self.report_date,
            "report_time": self.report_time.strftime("%H:%M:%S") if self.report_time else None,  
            "images": self.images,
            "status": self.status,
            "report_timestamp": self.report_timestamp.isoformat() if self.report_timestamp else None,  
            "updated_at": self.updated_at.isoformat() if self.updated_at else None  
        }