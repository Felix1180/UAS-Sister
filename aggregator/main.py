import time
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models, schemas, database
from datetime import datetime
from sqlalchemy.exc import OperationalError

app = FastAPI(title="Distributed Log Aggregator")
start_time = time.time()


# Fungsi untuk mencoba koneksi berulang kali (Bab 6: Failure Tolerance)
def init_db():
    retries = 5
    while retries > 0:
        try:
            models.Base.metadata.create_all(bind=database.engine)
            print("Database connected successfully!")
            break
        except OperationalError:
            retries -= 1
            print(f"Database not ready, retrying... ({retries} left)")
            time.sleep(2)

init_db()

# Inisialisasi Database
models.Base.metadata.create_all(bind=database.engine)

# Counter sederhana untuk stats (In-memory, untuk demo)
stats_counter = {"received": 0, "dropped": 0}

@app.get("/")
def read_root():
    return {
        "service": "aggregator-log-aggregator",
        "status": "active",
        "version": "1.0.0",
        "endpoints": ["/publish", "/events", "/stats", "/docs"]
    }

@app.post("/publish", status_code=status.HTTP_201_CREATED)
def publish_event(event: schemas.EventBase, db: Session = Depends(database.get_db)):
    global stats_counter
    stats_counter["received"] += 1
    
    try:
        # IMPLEMENTASI IDEMPOTENCY & TRANSAKSI (Bab 8-9)
        # Menggunakan session transaction sqlalchemy
        db_event = models.Event(**event.model_dump())
        db.add(db_event)
        db.commit() # Commit atomic
        return {"message": "Event processed successfully"}
    
    except IntegrityError:
        # Menangani duplikasi (Deduplication) secara transaksional
        db.rollback()
        stats_counter["dropped"] += 1
        # Mengembalikan status 200 (Bukan error) karena Idempotent
        return {"message": "Duplicate event ignored (idempotent)"}

@app.get("/events", response_model=list[schemas.EventResponse])
def get_events(topic: str = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Event)
    if topic:
        query = query.filter(models.Event.topic == topic)
    return query.all()

@app.get("/stats")
def get_stats(db: Session = Depends(database.get_db)):
    unique_count = db.query(models.Event).count()
    distinct_topics = db.query(models.Event.topic).distinct().all()
    
    return {
        "received": stats_counter["received"],
        "unique_processed": unique_count,
        "duplicate_dropped": stats_counter["dropped"],
        "topics": [t[0] for t in distinct_topics],
        "uptime_seconds": time.time() - start_time
    }