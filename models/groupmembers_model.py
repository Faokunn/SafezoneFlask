from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.base import Base

class GroupMember(Base):
    __tablename__ = 'group_members'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    circle_id = Column(Integer, ForeignKey('circle.id', ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="group_memberships")
    circle = relationship("Circle", back_populates="group_members")
