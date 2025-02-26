from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(80), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    type = Column(String(80), nullable=False)
    is_done = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications") 

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "type": self.type,
            "is_done": self.is_done
        }
