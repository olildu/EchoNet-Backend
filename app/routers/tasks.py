from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks & Coordination"])

@router.post("/accept")
def accept_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == task.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    new_task = models.Task(
        incident_id=task.incident_id,
        volunteer_id=task.volunteer_id,
        status=models.TaskStatus.ACCEPTED
    )
    
    if incident.status == models.IncidentStatus.PENDING:
        incident.status = models.IncidentStatus.ASSIGNED
        
    try:
        db.add(new_task)
        db.commit()
        return {"message": "Task accepted successfully", "task_id": str(new_task.id)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already accepted.")

# UPDATED: Fetch active task for the volunteer (Now includes evidence_url)
@router.get("/active/{volunteer_id}")
def get_active_task(volunteer_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(
        models.Task.volunteer_id == volunteer_id,
        models.Task.status != models.TaskStatus.COMPLETED,
        models.Task.status != models.TaskStatus.CANCELLED
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="No active mission found.")
    
    # We query the incident details linked to this task
    incident = db.query(
        models.Incident.id,
        models.Incident.category,
        models.Incident.description,
        models.Incident.status,
        models.Incident.reported_at,
        models.Incident.evidence_url, # NEW: Added to the query
        func.ST_Y(models.Incident.location).label("lat"),
        func.ST_X(models.Incident.location).label("lng")
    ).filter(models.Incident.id == task.incident_id).first()

    return {
        "task_id": task.id,
        "status": task.status,
        "incident": {
            "id": incident.id,
            "category": incident.category,
            "description": incident.description,
            "reported_at": incident.reported_at,
            "evidence_url": incident.evidence_url, # NEW: Passed to the frontend
            "latitude": incident.lat,
            "longitude": incident.lng
        }
    }

# Update mission status (EN_ROUTE -> ON_SCENE -> COMPLETED)
@router.put("/{task_id}/status")
def update_task_status(task_id: str, status: models.TaskStatus, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = status
    
    # Logic: If completed, set timestamp and resolve the underlying incident
    if status == models.TaskStatus.COMPLETED:
        task.completed_at = func.now()
        incident = db.query(models.Incident).filter(models.Incident.id == task.incident_id).first()
        if incident:
            incident.status = models.IncidentStatus.RESOLVED

    db.commit()
    return {"message": f"Status updated to {status.value}"}