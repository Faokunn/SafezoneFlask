from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Time, JSON, Date, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP
from datetime import datetime, timezone
from database.base import Base

class IncidentReportStatusHistory(Base):
    __tablename__ = 'incident_report_status_history'
    id = Column(Integer, primary_key=True)
    incident_report_id = Column(Integer, ForeignKey('incident_reports.id'), nullable=False)
    status = Column(String, nullable=False)  
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))  
    remarks = Column(Text, nullable=True)  

    incident_report = relationship("IncidentReport", back_populates="status_history")