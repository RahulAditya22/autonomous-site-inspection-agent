from app.agents.mission import MissionAgent
from app.agents.planner import PlanningAgent
from app.scoring.risk import score
from app.safety.rules import evaluate
def test_end_to_end_contract():
    tasks=MissionAgent().parse('Inspect A, B and C. Prioritize A.'); plan=PlanningAgent().plan(tasks,85); assert plan['waypoints']
    risk=score([{'label':'person','confidence':0.9},{'label':'car','confidence':0.8}])
    class T: battery=85; communication=True
    assert evaluate(T(),risk['recommended_action'])['allowed'] is True
