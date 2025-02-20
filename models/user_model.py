from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    # One-to-Many Relationships
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    contacts = relationship("ContactModel", back_populates="user", cascade="all, delete-orphan")
    sos_alerts = relationship("SOSAlerter", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    incident_reports = relationship("IncidentReport", back_populates="user", cascade="all, delete-orphan")
    safe_zones = relationship("SafeZone", back_populates="user", cascade="all, delete-orphan")

    # Many-to-Many Relationship via GroupMember
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan", overlaps="circles")
    circles = relationship("Circle", secondary="group_members", back_populates="members", overlaps="group_memberships")
