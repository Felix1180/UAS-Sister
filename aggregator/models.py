from sqlalchemy import Column, String, DateTime, JSON, UniqueConstraint, Integer
from database import Base

class Event(Base):
    __tablename__ = "events"

    # ID internal untuk database
    pk_id = Column(Integer, primary_key=True, index=True)
    # Data dari event
    topic = Column(String, index=True)
    event_id = Column(String, index=True)
    timestamp = Column(DateTime)
    source = Column(String)
    payload = Column(JSON)

    # DEDUP STRATEGY (Bab 9): Unique Constraint pada pasangan topic & event_id
    __table_args__ = (UniqueConstraint('topic', 'event_id', name='uix_topic_event_id'),)