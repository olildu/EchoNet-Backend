import httpx
import uuid
import asyncio
import random
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

async def run_e2e_test():
    # Use a random phone number every time to prevent "Already Registered" conflicts
    rand_phone_cit = f"9{random.randint(100000000, 999999999)}"
    rand_phone_vol = f"8{random.randint(100000000, 999999999)}"

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        print("🚀 Starting EchoNet E2E Test...")

        # 1. Register Citizen
        print(f"\n[Step 1] Registering Citizen with phone {rand_phone_cit}...")
        citizen_resp = await client.post("/auth/register", json={
            "full_name": "Test Citizen",
            "phone": rand_phone_cit,
            "password": "password123",
            "role": "CITIZEN"
        })
        
        if citizen_resp.status_code != 200:
            print(f"❌ Registration Failed (Status {citizen_resp.status_code})")
            print(f"Response Text: {citizen_resp.text}")
            return

        citizen_id = citizen_resp.json()["id"]

        # 2. Register Volunteer
        print(f"[Step 2] Registering Volunteer with phone {rand_phone_vol}...")
        volunteer_resp = await client.post("/auth/register", json={
            "full_name": "Test Volunteer",
            "phone": rand_phone_vol,
            "password": "password123",
            "role": "VOLUNTEER",
            "skills": ["MEDICAL"]
        })
        volunteer_id = volunteer_resp.json()["id"]

        # 3. Report Incident (滿足離線報告與任務分配需求)
        print("\n[Step 3] Citizen reporting emergency...")
        incident_id = str(uuid.uuid4())
        incident_data = {
            "id": incident_id,
            "reporter_id": citizen_id,
            "category": "MEDICAL",
            "description": "Heart attack symptoms.",
            "latitude": 26.8467,
            "longitude": 75.5613,
            "reported_at": datetime.now().isoformat()
        }
        resp = await client.post("/incidents/", json=incident_data)
        
        if resp.status_code == 200:
            print(f"✅ Incident Reported: {resp.json()['id']}")
        else:
            print(f"❌ Incident Failed (Status {resp.status_code}): {resp.text}")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())