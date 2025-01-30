from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    # Other relationships
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    contacts = relationship("ContactModel", back_populates="user", cascade="all, delete-orphan")
    sos_alerts = relationship("SOSAlerter", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    incident_reports = relationship("IncidentReport", back_populates="user", cascade="all, delete-orphan")

    # Many-to-many relationship with Circle through GroupMember
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")

    # Indirectly get all circles the user is part of
    circles = relationship("Circle", secondary="group_members", back_populates="members")
