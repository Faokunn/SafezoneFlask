from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.base import Base

class Circle(Base):
    __tablename__ = 'circle'



    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String(5), nullable=True)
    is_active = Column(Boolean, default=True)

    # Many-to-many relationship with User via GroupMember
    group_members = relationship("GroupMember", back_populates="circle", cascade="all, delete-orphan")

    # Indirectly get all users who are members of this circle
    members = relationship("User", secondary="group_members", back_populates="circles")
