from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
class Position(BaseModel):
    x: float
    y: float
    altitude: float = 20.0
class MissionTask(BaseModel):
    task_id: str
    location: str
    x: float
    y: float
    priority: Literal['low','normal','high','critical'] = 'normal'
    inspection_type: str = 'general site inspection'
    status: Literal['pending','active','completed','skipped'] = 'pending'
class MissionCreate(BaseModel):
    objective: str = Field(min_length=5, max_length=2000)
    drone_id: str = 'D-01'
class SafetyApproval(BaseModel):
    approved: bool
class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
class Detection(BaseModel):
    label: str
    confidence: float
    directly_observed: bool = True
    inferred: bool = False
    unknown: bool = False
    bbox: list[float] = Field(default_factory=list)
class PerceptionResult(BaseModel):
    detections: list[Detection]
    image_width: int
    image_height: int
    notes: list[str] = Field(default_factory=list)
    source: str = 'local-object-detector'
class RiskResult(BaseModel):
    severity: int
    risk_level: str
    reasons: list[str]
    recommended_action: str
class Decision(BaseModel):
    action: Literal['CONTINUE','REINSPECT','RETURN_HOME','HOLD_FOR_APPROVAL','ABORT']
    summary: str
    factors: list[str] = Field(default_factory=list)
    rag_sources: list[str] = Field(default_factory=list)
