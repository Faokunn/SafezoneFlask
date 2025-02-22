from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from database.base import Base

class Circle(Base):
    __tablename__ = 'circle'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String(5), nullable=True)
    is_active = Column(Boolean, default=False)
    code_expiry = Column(DateTime, nullable=True)


    # Many-to-Many Relationship via GroupMember
    group_members = relationship("GroupMember", back_populates="circle", cascade="all, delete-orphan", overlaps="members")
    members = relationship("User", secondary="group_members", back_populates="circles", overlaps="group_members")
