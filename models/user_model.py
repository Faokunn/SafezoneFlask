from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
from .association_tables import group_members  # Import the group_members table

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    notifications = relationship("Notification", back_populates="users", cascade="all, delete-orphan")
    contacts = relationship("ContactModel", back_populates="user", cascade="all, delete-orphan")
    sos_alerts = relationship("SOSAlerter", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    incident_reports = relationship("IncidentReport", back_populates="user", cascade="all, delete-orphan")

    circles = relationship(
        "Circle", 
        secondary=group_members, 
        back_populates="members"
    )
