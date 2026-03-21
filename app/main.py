import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # NEW IMPORT
from app.database import engine, Base
from app.routers import auth, incidents, matching, websockets, tasks, chat

# Ensure the uploads directory exists
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EchoNet API", version="1.0")

# NEW: Mount the uploads folder to serve files as static assets
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(matching.router)
app.include_router(tasks.router)
app.include_router(chat.router)
app.include_router(websockets.router)

@app.get("/")
def health_check():
    return {"status": "EchoNet Backend is online"}