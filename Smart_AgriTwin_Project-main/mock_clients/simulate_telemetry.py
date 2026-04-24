import requests, time, random, uuid
API = "http://localhost:5000/api/telemetry/ingest"
device_uid = "dev-sim-1"

def send(payload):
    data = {"device_uid": device_uid, "payload": payload}
    r = requests.post(API, json=data)
    print(r.status_code, r.text)

if __name__ == "__main__":
    while True:
        payload = {
            "temperature": round(20 + random.uniform(-2, 5) + (0.1 * (time.time()%60)), 2),
            "humidity": round(40 + random.uniform(-5, 5), 2),
            "soil_moisture": round(30 + random.uniform(-4, 4), 2)
        }
        send(payload)
        time.sleep(10)
