import httpx
import time
import random
import uuid
from datetime import datetime

TARGET_URL = "http://aggregator:8000/publish"

def generate_event(event_id=None):
    return {
        "topic": random.choice(["sensor_data", "user_logs", "error_reports"]),
        "event_id": event_id or str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "source": "publisher-sim-01",
        "payload": {"value": random.random(), "status": "active"}
    }

def run_simulation():
    print("Starting simulation with 30% duplication...")
    processed_ids = []
    
    with httpx.Client() as client:
        for i in range(20000): # Sesuai syarat performa UAS
            # Logika duplikasi
            if random.random() < 0.3 and processed_ids:
                event = generate_event(event_id=random.choice(processed_ids))
            else:
                event = generate_event()
                processed_ids.append(event["event_id"])
                if len(processed_ids) > 1000: processed_ids.pop(0)

            try:
                client.post(TARGET_URL, json=event)
            except Exception as e:
                print(f"Error: {e}")
            
            if i % 1000 == 0:
                print(f"Sent {i} events...")

if __name__ == "__main__":
    time.sleep(5) # Tunggu aggregator siap
    run_simulation()