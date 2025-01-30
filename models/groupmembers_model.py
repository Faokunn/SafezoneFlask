from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class GroupMember(Base):
    __tablename__ = 'group_members'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    circle_id = Column(Integer, ForeignKey('circle.id'), nullable=False)

    user = relationship("User", back_populates="circles")
    circle = relationship("Circle", back_populates="members")
