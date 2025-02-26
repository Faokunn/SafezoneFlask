from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    address = Column(String(80), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_girl = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    status = Column(String, default="Safe")
    latitude = Column(Float, nullable=False, default=0.0)
    longitude = Column(Float, nullable=False, default=0.0)
    circle = Column(Integer, nullable=True)
    profile_picture_url = Column(String, nullable=True)  
    user = relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "is_admin": self.is_admin,
            "is_girl": self.is_girl,
            "is_verified": self.is_verified,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "profile_picture_url": self.profile_picture_url,
            "circle": self.circle
        }
