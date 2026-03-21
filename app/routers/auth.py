from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])

@router.post("/register", response_model=schemas.Token)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    new_user = models.User(
        full_name=user.full_name,
        phone=user.phone,
        password_hash=user.password, 
        role=user.role,
        age=user.age,
        national_id=user.national_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if user.role == models.UserRole.VOLUNTEER and user.skills:
        unique_skills = set(user.skills)
        for skill in unique_skills:
            db_skill = models.VolunteerSkill(volunteer_id=new_user.id, skill=skill)
            db.add(db_skill)
        db.commit()

    return {"access_token": "hackathon_mock_token", "token_type": "bearer", "user_id": new_user.id, "user_role": new_user.role.name, "full_name": new_user.full_name}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if not db_user or db_user.password_hash != user.password:
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    
    return {"access_token": "hackathon_mock_token", "token_type": "bearer", "user_id": db_user.id, "user_role": db_user.role.name, "full_name": db_user.full_name}

@router.post("/users/{user_id}/contacts")
def create_emergency_contact(user_id: str, contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.EmergencyContact(
        user_id=user_id,
        name=contact.name,
        phone=contact.phone,
        is_primary=contact.is_primary
    )
    db.add(db_contact)
    db.commit()
    return {"status": "Contact saved"}

# NEW: Endpoint to fetch the citizen's saved contacts
@router.get("/users/{user_id}/contacts")
def get_emergency_contacts(user_id: str, db: Session = Depends(get_db)):
    contacts = db.query(models.EmergencyContact).filter(models.EmergencyContact.user_id == user_id).all()
    return [{"id": str(c.id), "name": c.name, "phone": c.phone, "is_primary": c.is_primary} for c in contacts]

@router.get("/users/{user_id}/stats")
def get_volunteer_stats(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    completed_tasks = db.query(models.Task).filter(
        models.Task.volunteer_id == user_id, 
        models.Task.status == models.TaskStatus.COMPLETED
    ).all()
    
    total_hours = 0
    for task in completed_tasks:
        if task.completed_at and task.assigned_at:
            duration = task.completed_at - task.assigned_at
            total_hours += duration.total_seconds() / 3600

    active = db.query(models.Task).filter(
        models.Task.volunteer_id == user_id, 
        models.Task.status.in_([models.TaskStatus.ACCEPTED, models.TaskStatus.EN_ROUTE, models.TaskStatus.ON_SCENE])
    ).count()
    
    skills_query = db.query(models.VolunteerSkill.skill).filter(models.VolunteerSkill.volunteer_id == user_id).all()
    skills = [s[0].name for s in skills_query] if skills_query else ["GENERAL"]

    return {
        "tasks_completed": len(completed_tasks), 
        "active_tasks": active, 
        "hours_logged": round(total_hours, 1),
        "phone": user.phone,
        "age": user.age,
        "skills": skills
    }