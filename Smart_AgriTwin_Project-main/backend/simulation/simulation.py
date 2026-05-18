import os
import time
import random
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

SIM_TOKEN = os.getenv("SIM_TOKEN")

DEVICES = [

    {"uid": "dev1", "zone_id": 1},
    {"uid": "dev2", "zone_id": 1},
    {"uid": "dev3", "zone_id": 1},

    {"uid": "dev4", "zone_id": 2},
    {"uid": "dev5", "zone_id": 2},
    {"uid": "dev6", "zone_id": 2},

    {"uid": "dev7", "zone_id": 3},
    {"uid": "dev8", "zone_id": 3},
    {"uid": "dev9", "zone_id": 3},

    {"uid": "dev10", "zone_id": 4},
    {"uid": "dev11", "zone_id": 4},
    {"uid": "dev12", "zone_id": 4},
    {"uid": "dev13", "zone_id": 4},
]

if not SIM_TOKEN:
    print("❌ ERROR: SIM_TOKEN missing in .env file")
    exit()

print("🔌 Simulation script started")
for d in DEVICES:
    print(f"🆔 Device UID: {d['uid']} (Zone {d['zone_id']})")
print(f"🔑 SIM Token Loaded")
print("--------------------------------------------------")


def generate_payload(device_uid):
    return {
        "device_uid": device_uid,
        "temperature": round(random.uniform(18, 30), 2),
        "humidity": round(random.uniform(40, 80), 2),
        "soil_moisture": round(random.uniform(20, 80), 2),
        "timestamp": None
    }


while True:
    for d in DEVICES:
        payload = generate_payload(d["uid"])

        print(f"\n📡 Sending from {d['uid']}: {payload}")

        try:
            response = requests.post(
                API_URL,
                json=payload,
                headers={"Sim-Token": SIM_TOKEN}
            )
        except Exception as e:
            print(f"❌ Connection error: {e}")
            continue

        if response.status_code == 201:
            print(f"✅ {d['uid']} accepted")
        else:
            print(f"⚠ {d['uid']} error {response.status_code}")

    time.sleep(3)
