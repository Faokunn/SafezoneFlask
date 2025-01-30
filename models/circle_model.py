from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.base import Base

class Circle(Base):
    __tablename__ = 'circle'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Many-to-many relationship between Circle and User through group_members
    members = relationship("User", secondary="group_members", back_populates="circles")

