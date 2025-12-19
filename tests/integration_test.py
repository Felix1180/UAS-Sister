import pytest
import httpx
import uuid
from datetime import datetime

BASE_URL = "http://aggregator:8000"

def test_1_root_health():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert response.json()["status"] == "active"

def test_2_stats_initial_check():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/stats")
        assert response.status_code == 200

def test_3_valid_publish():
    payload = {
        "topic": "test_topic",
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "source": "pytest",
        "payload": {"data": "unit test"}
    }
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/publish", json=payload)
        assert response.status_code == 201

def test_4_idempotency_duplicate_id():
    event_id = "unique-id-123"
    payload = {
        "topic": "test_topic",
        "event_id": event_id,
        "timestamp": datetime.now().isoformat(),
        "source": "pytest",
        "payload": {}
    }
    with httpx.Client() as client:
        # Kirim pertama
        client.post(f"{BASE_URL}/publish", json=payload)
        # Kirim kedua (duplikat)
        response = client.post(f"{BASE_URL}/publish", json=payload)
        assert "ignored" in response.json()["message"]

def test_5_invalid_schema_missing_topic():
    payload = {"event_id": "123"}
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/publish", json=payload)
        assert response.status_code == 422

def test_6_invalid_schema_missing_id():
    payload = {"topic": "test"}
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/publish", json=payload)
        assert response.status_code == 422

def test_7_get_events_list():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

def test_8_filter_by_topic():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/events?topic=test_topic")
        assert response.status_code == 200

def test_9_stats_increment_check():
    with httpx.Client() as client:
        before = client.get(f"{BASE_URL}/stats").json()["unique_processed"]
        # Publish satu data baru
        client.post(f"{BASE_URL}/publish", json={
            "topic": "test", "event_id": str(uuid.uuid4()), 
            "timestamp": datetime.now().isoformat(), "source": "test", "payload": {}
        })
        after = client.get(f"{BASE_URL}/stats").json()["unique_processed"]
        assert after == before + 1

def test_10_large_payload():
    payload = {
        "topic": "heavy", "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(), "source": "test",
        "payload": {"data": "x" * 1000}
    }
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/publish", json=payload)
        assert response.status_code == 201

def test_11_uptime_is_number():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/stats")
        assert isinstance(response.json()["uptime_seconds"], float)

def test_12_docs_accessible():
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/docs")
        assert response.status_code == 200