<p align="center">
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/assets/images/logo/app_logo.png?raw=true" 
       alt="EchoNet Logo" 
       width="180">
</p>

# ⚙️ EchoNet Backend: Tactical Coordination Engine

The high-performance core of the EchoNet network. Built with **FastAPI** and **PostgreSQL/PostGIS**, this backend serves as the tactical command center, handling spatial matching, real-time synchronization, and mission lifecycle management.

## 📺 Demo

<p align="center">
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/echonet_demo.gif?raw=true" width="500">
</p>

<p align="center">
  <a href="https://youtu.be/HdIgbg-pKwM">
    ▶️ Watch Full Demo on YouTube
  </a>
</p>

## 📸 Screenshots

<p align="center">
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/5caeeb07-faf8-4377-9180-fc9bc9e66aa3.jpg?raw=true" width="250"/>
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/6ef6ba01-a786-4a20-9f16-51134077637e.jpg?raw=true" width="250"/>
</p>

<p align="center">
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/711fc0cc-8dbb-408b-aa06-142a84430add.jpg?raw=true" width="250"/>
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/7645da67-02bc-47d2-a7c1-3467fb82225b.jpg?raw=true" width="250"/>
</p>

<p align="center">
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/a78105fe-870b-45b0-9bd0-b5dda60c78c1.jpg?raw=true" width="250"/>
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/a81596ce-e538-4a87-b1e6-4a061d6bebea.jpg?raw=true" width="250"/>
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/b4e59832-3876-481b-9551-35e1667d2187.jpg?raw=true" width="250"/>
</p>

<p align="center">
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/be9037d6-1e31-4482-9f7a-07e1806ce957.jpg?raw=true" width="250"/>
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/dfc597fe-b216-4b50-a287-390b74f023fd.jpg?raw=true" width="250"/>
  <img src="https://github.com/olildu/EchoNet-Frontend/blob/main/project_assets/e7a4bc67-f8e5-446f-8de2-a8a076fcbb98.jpg?raw=true" width="250"/>
</p>

## 🌟 Technical Highlights & Differentiators

The backend is engineered for low-latency disaster response coordination using modern Python asynchronous paradigms.

| Feature | Technical Implementation | Engineering Value |
| :--- | :--- | :--- |
| **Spatial Intelligence** | **PostGIS** + **GeoAlchemy2** | High-performance geometric queries for nearest-responder matching. |
| **Real-Time Push** | **WebSockets** (Event Bus Pattern) | Instant broadcast of SOS alerts and messages to the volunteer mesh. |
| **Mission Lifecycle** | **SQLAlchemy** State Machine | Strict integrity from PENDING ➔ ASSIGNED ➔ RESOLVED states. |
| **Async Architecture** | **FastAPI** + **Uvicorn** | Non-blocking I/O capable of handling high-concurrency during mass emergencies. |


## 🧱 System Architecture

The project follows a modular router-based architecture for clear separation of concerns.

### **Core Components**
- **Data Layer (`models.py`)**: Defines the relational and spatial schema, including `Geometry(POINT)` fields for real-time location tracking.
- **API Layer (`routers/`)**: Specialized modules for Auth, Incidents, Tasks, and Chat.
- **Real-Time Layer (`websockets.py`)**: A centralized `ConnectionManager` that handles active socket persistence and global broadcasts.
- **Validation Layer (`schemas.py`)**: Uses **Pydantic** for strict request/response data integrity.


## ⚙️ Tactical Modules

| Module | Purpose | Key Technical Implementation |
| :--- | :--- | :--- |
| **Incident Engine** | SOS Processing | Converts GPS coordinates to WKT Elements for spatial storage. |
| **Spatial Matching** | Responder Triage | Uses PostGIS raw SQL for `<->` (Distance) operators for maximum speed. |
| **Comms Hub** | Secure Messaging | Bi-directional socket communication with persistent message logging. |
| **Evidence API** | Field Intelligence | Handles multipart file uploads for scene verification photos. |


## 🛠 Deep Technical Deep-Dive

### 📡 The WebSocket Event Bus
EchoNet uses a "Ping-and-Fetch" pattern. When a user reports an incident, the backend triggers `manager.broadcast()`. This sends a lightweight JSON signal to all connected volunteers, who then trigger an atomic BLoC refresh. This maintains high synchronization with minimal data overhead.

### 📍 PostGIS Spatial Matching
The backend performs nearest-neighbor searches using raw SQL for performance. It filters active volunteers by both **geographical proximity** and **specific skill sets** (e.g., matching a "Medical" skill to a "Medical" incident) in a single query execution.

### 🛡 Mission Integrity
To prevent double-assignment, the database enforces a `UniqueConstraint` on the `volunteer_id` and `incident_id` within the `tasks` table. The status transition from `EN_ROUTE` to `COMPLETED` automatically triggers the resolution of the parent incident.


## 🛠️ Development Setup

Requires **Python 3.10+** and **PostgreSQL with PostGIS**.

### **Prerequisites**
- Docker (for PostGIS)
- Python environment

### **Installation**

#### 1️⃣ Start PostGIS Database
```bash
docker run --name echonet-db -e POSTGRES_PASSWORD=localpassword -p 5432:5432 -d postgis/postgis
```
#### 2️⃣ Setup Backend

```bash
git clone https://github.com/olildu/echonet-backend.git
cd echonet-backend
pip install -r requirements.txt
```

#### 3️⃣ Run Tactical Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📺 Dashboard Overview

The backend automatically serves the Field Intelligence images captured by citizens. These are accessible via the `/uploads` static route for responders.
