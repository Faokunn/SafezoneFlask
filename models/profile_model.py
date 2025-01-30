from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class Profile(Base):
    __tablename__ = 'Profile'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    address = Column(String(80), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_girl = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="profile")