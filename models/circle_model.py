from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from database.base import Base

class Circle(Base):
    __tablename__ = 'circle'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String(5), nullable=True)
    code_expiry = Column(DateTime, nullable=True)

    # Many-to-Many Relationship via GroupMember
    group_members = relationship("GroupMember", back_populates="circle", cascade="all, delete-orphan", overlaps="members")
    members = relationship("User", secondary="group_members", back_populates="circles", overlaps="group_members")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "code_expiry": self.code_expiry.isoformat() if self.code_expiry else None,
            "group_members": [member.to_dict() for member in self.group_members] if self.group_members else []
        }
