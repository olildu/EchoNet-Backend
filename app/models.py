import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base

class UserRole(enum.Enum):
    CITIZEN = 'CITIZEN'
    VOLUNTEER = 'VOLUNTEER'
    AUTHORITY = 'AUTHORITY'
    NGO = 'NGO'

class EmergencyCategory(enum.Enum):
    MEDICAL = 'MEDICAL'
    FIRE = 'FIRE'
    RESCUE = 'RESCUE'
    FLOOD = 'FLOOD'
    FOOD_SUPPLY = 'FOOD_SUPPLY'
    SHELTER = 'SHELTER'
    MENTAL_HEALTH = 'MENTAL_HEALTH'
    INFRASTRUCTURE = 'INFRASTRUCTURE'
    MISSING_PERSON = 'MISSING_PERSON'
    GENERAL = 'GENERAL'

class IncidentStatus(enum.Enum):
    PENDING = 'PENDING'
    ASSIGNED = 'ASSIGNED'
    IN_PROGRESS = 'IN_PROGRESS'
    ESCALATED = 'ESCALATED'
    RESOLVED = 'RESOLVED'

class TaskStatus(enum.Enum):
    ACCEPTED = 'ACCEPTED'
    EN_ROUTE = 'EN_ROUTE'
    ON_SCENE = 'ON_SCENE'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(Enum(UserRole), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # New Extended Profile Fields
    age = Column(Integer, nullable=True)
    national_id = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    is_primary = Column(Boolean, default=False)

class VolunteerSkill(Base):
    __tablename__ = "volunteer_skills"
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    skill = Column(Enum(EmergencyCategory), primary_key=True)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    synced_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    is_sms_fallback = Column(Boolean, default=False)
    category = Column(Enum(EmergencyCategory), nullable=False)
    description = Column(Text)
    evidence_url = Column(String(500), nullable=True) # New Photo Upload Field
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.PENDING)
    required_volunteers = Column(Integer, default=1)
    reported_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"))
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(Enum(TaskStatus), default=TaskStatus.ACCEPTED)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint('volunteer_id', 'incident_id', name='unique_volunteer_incident'),)

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"))
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    is_system_alert = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class VolunteerLocation(Base):
    __tablename__ = "volunteer_locations"
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())