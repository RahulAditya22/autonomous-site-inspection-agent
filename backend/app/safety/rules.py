from app.config.settings import settings
from app.agents.core import SafetyRules
_default=SafetyRules(settings.min_return_battery,settings.critical_battery)
def evaluate(telemetry,recommended_action): return _default.evaluate(telemetry,recommended_action)
