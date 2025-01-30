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