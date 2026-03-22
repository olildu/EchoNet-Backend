import os
import shutil
import json # NEW IMPORT

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.elements import WKTElement
from typing import List
from app import models, schemas
from app.database import get_db
from app.routers.websockets import manager # NEW IMPORT

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("/all")
def get_all_incidents(db: Session = Depends(get_db)):
    # Fetch all incidents ordered by newest first
    incidents = db.query(models.Incident).order_by(models.Incident.reported_at.desc()).all()
    
    # Return custom dict to bypass strict schema limits temporarily for the dashboard
    return [{
        "id": str(i.id),
        "category": i.category.value,
        "status": i.status.value,
        "description": i.description,
        "reported_at": i.reported_at.isoformat() if i.reported_at else None
    } for i in incidents]

# UPDATED: Changed to async def to support awaiting the websocket broadcast
@router.post("/", response_model=schemas.IncidentResponse)
async def report_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    point_wkt = f"POINT({incident.longitude} {incident.latitude})"
    new_incident = models.Incident(
        id=incident.id,
        reporter_id=incident.reporter_id,
        synced_by_id=incident.synced_by_id,
        is_sms_fallback=incident.is_sms_fallback,
        category=incident.category,
        description=incident.description,
        location=WKTElement(point_wkt, srid=4326),
        required_volunteers=incident.required_volunteers,
        reported_at=incident.reported_at
    )
    db.add(new_incident)
    try:
        db.commit()
        db.refresh(new_incident)
        
        # WOW FACTOR: Instantly notify all connected volunteer apps to refresh their task lists!
        await manager.broadcast(json.dumps({"type": "NEW_INCIDENT"}))
        
        return schemas.IncidentResponse(
            id=new_incident.id,
            category=new_incident.category,
            status=new_incident.status,
            description=new_incident.description,
            reported_at=new_incident.reported_at,
            latitude=incident.latitude,
            longitude=incident.longitude
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/{user_id}", response_model=List[schemas.IncidentResponse])
def get_my_reports(user_id: str, db: Session = Depends(get_db)):
    results = db.query(
        models.Incident.id,
        models.Incident.category,
        models.Incident.status,
        models.Incident.description,
        models.Incident.reported_at,
        func.ST_Y(models.Incident.location).label("lat"),
        func.ST_X(models.Incident.location).label("lng")
    ).filter(models.Incident.reporter_id == user_id).order_by(models.Incident.created_at.desc()).all()
    
    incidents = []
    for row in results:
        incidents.append(schemas.IncidentResponse(
            id=row.id,
            category=row.category,
            status=row.status,
            description=row.description,
            reported_at=row.reported_at,
            latitude=row.lat,
            longitude=row.lng
        ))
        
    return incidents

@router.post("/{incident_id}/evidence")
async def upload_evidence(incident_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    upload_folder = "uploads"
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{incident_id}{file_extension}"
    file_path = os.path.join(upload_folder, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    base_url = "http://192.168.137.1:8000" 
    access_url = f"{base_url}/uploads/{unique_filename}"
    
    incident.evidence_url = access_url
    db.commit()
    
    # Also broadcast when an image is attached so the volunteer sees it instantly
    await manager.broadcast(json.dumps({"type": "NEW_INCIDENT"}))
    
    return {"message": "Evidence uploaded successfully", "url": access_url}

@router.get("/pending", response_model=List[schemas.IncidentResponse])
def get_pending_incidents(db: Session = Depends(get_db)):
    results = db.query(
        models.Incident.id,
        models.Incident.category,
        models.Incident.status,
        models.Incident.description,
        models.Incident.reported_at,
        func.ST_Y(models.Incident.location).label("lat"),
        func.ST_X(models.Incident.location).label("lng")
    ).filter(
        models.Incident.status == models.IncidentStatus.PENDING
    ).order_by(models.Incident.created_at.desc()).all()
    
    incidents = []
    for row in results:
        incidents.append(schemas.IncidentResponse(
            id=row.id,
            category=row.category,
            status=row.status,
            description=row.description,
            reported_at=row.reported_at,
            latitude=row.lat,
            longitude=row.lng
        ))
        
    return incidents