from .core import SafetyRules as _Rules
class SafetyAgent:
    def __init__(self,rag): self.rag=rag; self.rules=_Rules()
    def decide(self,telemetry,recommended_action,context=''):
        policy=self.rag.retrieve(context or 'emergency inspection safety battery return fire smoke'); gate=self.rules.evaluate(telemetry,recommended_action); source=policy[0]['source'] if policy else 'local safety rules'
        return {'gate':gate,'rag':policy,'summary':f"{gate['reason']} Guidance source: {source}."}
