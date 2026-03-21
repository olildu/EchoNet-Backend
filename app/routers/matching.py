from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from geoalchemy2.functions import ST_Distance, ST_SetSRID, ST_MakePoint
import app.models as models
from app.database import get_db

router = APIRouter(prefix="/matching", tags=["Matching"])

@router.get("/nearest-volunteers/{incident_id}")
def get_nearest_volunteers(incident_id: str, limit: int = 5, db: Session = Depends(get_db)):
    # 1. Get the incident's location and category
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}

    # 2. The PostGIS Query: Find active volunteers with the right skill, ordered by distance
    # We use raw SQL here for maximum spatial performance
    query = text("""
        SELECT u.id, u.full_name, u.phone, 
               ST_Distance(v.location, i.location, true) AS distance_meters
        FROM volunteer_locations v
        JOIN users u ON v.volunteer_id = u.id
        JOIN volunteer_skills s ON u.id = s.volunteer_id
        JOIN incidents i ON i.id = :incident_id
        WHERE u.is_active = true 
          AND s.skill = i.category
        ORDER BY v.location <-> i.location
        LIMIT :limit
    """)
    
    results = db.execute(query, {"incident_id": incident_id, "limit": limit}).fetchall()
    
    volunteers = []
    for row in results:
        volunteers.append({
            "id": str(row.id),
            "name": row.full_name,
            "distance_meters": round(row.distance_meters, 2)
        })
        
    return {"incident": incident.category, "nearest_volunteers": volunteers}