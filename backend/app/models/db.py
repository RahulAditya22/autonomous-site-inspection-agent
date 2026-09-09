from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from app.config import settings
class Base(DeclarativeBase): pass
class Drone(Base):
    __tablename__='drones'
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), default='available')
    battery: Mapped[float] = mapped_column(Float, default=100)
    x: Mapped[float] = mapped_column(Float, default=0)
    y: Mapped[float] = mapped_column(Float, default=0)
    altitude: Mapped[float] = mapped_column(Float, default=0)
    speed: Mapped[float] = mapped_column(Float, default=12)
    communication: Mapped[bool] = mapped_column(Boolean, default=True)
    camera_status: Mapped[str] = mapped_column(String(32), default='ready')
    health: Mapped[str] = mapped_column(String(32), default='nominal')
    current_task: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mission_status: Mapped[str] = mapped_column(String(32), default='idle')
class Mission(Base):
    __tablename__='missions'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    objective: Mapped[str] = mapped_column(Text)
    drone_id: Mapped[str] = mapped_column(ForeignKey('drones.id'))
    status: Mapped[str] = mapped_column(String(32), default='planned')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    route_json: Mapped[str] = mapped_column(Text, default='[]')
    final_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    tasks = relationship('Task', back_populates='mission', cascade='all, delete-orphan')
    events = relationship('MissionEvent', back_populates='mission', cascade='all, delete-orphan')
    inspections = relationship('Inspection', back_populates='mission', cascade='all, delete-orphan')
class Task(Base):
    __tablename__='tasks'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey('missions.id'))
    location: Mapped[str] = mapped_column(String(128))
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    priority: Mapped[str] = mapped_column(String(16), default='normal')
    inspection_type: Mapped[str] = mapped_column(String(128), default='general site inspection')
    status: Mapped[str] = mapped_column(String(24), default='pending')
    mission = relationship('Mission', back_populates='tasks')
class MissionEvent(Base):
    __tablename__='mission_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey('missions.id'))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    agent: Mapped[str] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(64))
    summary: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[str] = mapped_column(Text, default='{}')
    mission = relationship('Mission', back_populates='events')
class Inspection(Base):
    __tablename__='inspections'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey('missions.id'))
    task_id: Mapped[str] = mapped_column(String(64))
    image_path: Mapped[str] = mapped_column(Text)
    detections_json: Mapped[str] = mapped_column(Text, default='[]')
    risk_json: Mapped[str] = mapped_column(Text, default='{}')
    decision_json: Mapped[str] = mapped_column(Text, default='{}')
    mission = relationship('Mission', back_populates='inspections')
engine = create_engine(settings.database_url, connect_args={'check_same_thread': False} if settings.database_url.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
def init_db(): Base.metadata.create_all(engine)
