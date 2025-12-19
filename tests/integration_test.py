import pytest
import httpx
import uuid
from datetime import datetime

BASE_URL = "http://aggregator:8000"

def test_health_check():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/stats")
        assert response.status_code == 200

def test_deduplication_logic():
    # Kirim event yang sama 2x
    event_id = str(uuid.uuid4())
    payload = {
        "topic": "test",
        "event_id": event_id,
        "timestamp": datetime.now().isoformat(),
        "source": "test-suite",
        "payload": {}
    }
    with httpx.Client() as client:
        r1 = client.post(f"{BASE_URL}/publish", json=payload)
        r2 = client.post(f"{BASE_URL}/publish", json=payload)
        
        assert r1.status_code == 201
        assert "successfully" in r1.json()["message"]
        assert r2.status_code == 201 # Idempotent returns 201/200
        assert "ignored" in r2.json()["message"]

def test_stats_consistency():
    with httpx.Client() as client:
        res = client.get(f"{BASE_URL}/stats")
        data = res.json()
        assert "unique_processed" in data
        assert data["unique_processed"] >= 0

# Tambahkan test lain sampai 12-20 test sesuai instruksi
# Contoh: test_invalid_schema, test_topic_filtering, dll.