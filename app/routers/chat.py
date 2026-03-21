import json # NEW IMPORT
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.routers.websockets import manager # NEW IMPORT

router = APIRouter(prefix="/chat", tags=["Messaging"])

# UPDATED: Changed to async def
@router.post("/{incident_id}/messages", response_model=schemas.MessageResponse)
async def send_message(incident_id: str, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    new_msg = models.Message(
        incident_id=incident_id,
        sender_id=message.sender_id,
        content=message.content,
        is_system_alert=message.is_system_alert
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    # WOW FACTOR: Instantly push the new message down the websocket
    await manager.broadcast(json.dumps({
        "type": "NEW_MESSAGE", 
        "incident_id": incident_id
    }))
    
    return new_msg

@router.get("/{incident_id}/messages", response_model=List[schemas.MessageResponse])
def get_messages(incident_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.incident_id == incident_id).order_by(models.Message.timestamp.asc()).all()
    return messages