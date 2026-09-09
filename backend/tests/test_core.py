from pathlib import Path
from app.agents.mission import MissionAgent
from app.agents.planner import PlanningAgent
from app.scoring.risk import score
from app.safety.rules import evaluate
from app.simulator.controller import SimulatedDroneController
from app.rag.store import RAGStore
def test_mission_parser_and_priority():
    tasks=MissionAgent().parse('Inspect locations A, B and C. Prioritize A.'); assert len(tasks)==3; assert tasks[0].priority=='high'
def test_planner_uses_distance_and_battery():
    plan=PlanningAgent().plan(MissionAgent().parse('Inspect A B C'),85); assert plan['distance']>0; assert plan['battery_required']>0; assert plan['feasible'] is True
def test_risk_is_deterministic_and_explainable():
    result=score([{'label':'person','confidence':.92},{'label':'smoke','confidence':.91}]); assert result['severity']>=4; assert result['reasons']
def test_safety_overrides_low_battery():
    d=SimulatedDroneController('D-01',battery=12); d.takeoff(); gate=evaluate(d.get_telemetry(),'CONTINUE'); assert gate['allowed'] is False; assert gate['action']=='ABORT'
def test_rag_returns_real_source():
    hits=RAGStore(Path('data/knowledge')).retrieve('communication loss'); assert hits; assert hits[0]['source']=='drone_operations.md'
