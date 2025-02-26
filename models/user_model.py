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

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            #"notifications": [notification.to_dict() for notification in self.notifications] if self.notifications else [],
            #"contacts": [contact.to_dict() for contact in self.contacts] if self.contacts else [],
            "sos_alerts": [sos_alert.to_dict() for sos_alert in self.sos_alerts] if self.sos_alerts else [],
            "profile": self.profile.to_dict() if self.profile else None,
            "incident_reports": [incident.to_dict() for incident in self.incident_reports] if self.incident_reports else [],
            "safe_zones": [safe_zone.to_dict() for safe_zone in self.safe_zones] if self.safe_zones else [],
            "group_memberships": [membership.to_dict() for membership in self.group_memberships] if self.group_memberships else [],
            "circles": [circle.to_dict() for circle in self.circles] if self.circles else []
    }
