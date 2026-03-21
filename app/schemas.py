from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models import UserRole, EmergencyCategory, IncidentStatus, TaskStatus

class UserCreate(BaseModel):
    full_name: str
    phone: str
    password: str
    role: UserRole
    age: Optional[int] = None
    national_id: Optional[str] = None
    skills: Optional[List[EmergencyCategory]] = [] 

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    user_role: str
    full_name: str

class ContactCreate(BaseModel):
    name: str
    phone: str
    is_primary: bool = False

class IncidentCreate(BaseModel):
    id: UUID  
    reporter_id: UUID
    synced_by_id: Optional[UUID] = None
    is_sms_fallback: bool = False
    category: EmergencyCategory
    description: str
    latitude: float
    longitude: float
    required_volunteers: int = 1
    reported_at: datetime

# UPDATED: Added reported_at, latitude, and longitude for the frontend dashboards
class IncidentResponse(BaseModel):
    id: UUID
    category: EmergencyCategory
    status: IncidentStatus
    description: str
    reported_at: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    incident_id: UUID
    volunteer_id: UUID

class MessageCreate(BaseModel):
    sender_id: UUID
    content: str
    is_system_alert: bool = False

class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    content: str
    is_system_alert: bool
    timestamp: datetime
    class Config:
        from_attributes = True