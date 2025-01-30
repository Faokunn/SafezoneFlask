from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base
from .association_tables import group_members  # Import the group_members table

class Circle(Base):
    __tablename__ = 'circle'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Many-to-many relationship between Circle and User
    members = relationship(
        "User", 
        secondary=group_members, 
        back_populates="circles"
    )
