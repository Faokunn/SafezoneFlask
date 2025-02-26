from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class SOSAlerter(Base):
    __tablename__ = 'sos_alerts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    alert_time = Column(Time, default=datetime.now().time)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(80), nullable=False)

    user = relationship("User", back_populates="sos_alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "alert_time": self.alert_time.isoformat() if self.alert_time else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status
        }
