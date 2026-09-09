from __future__ import annotations
import re
from uuid import uuid4
from app.models.schemas import MissionTask
from app.simulator.calculations import route_distance, estimate_battery
LOCATIONS={'a':(18,8),'b':(42,18),'c':(62,42),'d':(30,52),'e':(72,14),'north gate':(12,48),'warehouse':(55,10),'crane':(68,46),'tower':(25,35)}
PRIORITY={'critical':0,'high':1,'normal':2,'low':3}
class MissionAgent:
    def parse(self,objective):
        lower=objective.lower(); names=[]
        for token in re.findall(r'\b(?:location\s*)?([a-e])\b',lower):
            v=token.upper()
            if v not in names: names.append(v)
        for phrase in LOCATIONS:
            if len(phrase)>1 and phrase in lower and phrase.title() not in names: names.append(phrase.title())
        if not names: names=['A','B','C','D']
        return [MissionTask(task_id=str(uuid4())[:8],location=n,x=LOCATIONS.get(n.lower(),(18+i*16,10+i*12))[0],y=LOCATIONS.get(n.lower(),(18+i*16,10+i*12))[1],priority='high' if re.search(rf'priorit(?:y|ize|ise).*\b{n.lower()}\b',lower) or re.search(rf'\b{n.lower()}\b.*\bpriorit',lower) else 'normal') for i,n in enumerate(names)]
class PlanningAgent:
    def plan(self,tasks,battery,speed=12):
        ordered=sorted(tasks,key=lambda t:(PRIORITY[t.priority],t.location)); pts=[(0,0)]+[(t.x,t.y) for t in ordered]+[(0,0)]; total=route_distance(pts); required=estimate_battery(total)
        return {'tasks':ordered,'waypoints':[(t.x,t.y) for t in ordered],'distance':round(total,2),'battery_required':round(required,2),'feasible':battery>=required,'estimated_minutes':round(total/speed,2)}
    def replan(self,tasks,current_pos,battery,speed=12):
        pending=[t for t in tasks if t.status=='pending']; pts=[current_pos]+[(t.x,t.y) for t in pending]+[(0,0)]; total=route_distance(pts); required=estimate_battery(total)
        return {'tasks':pending,'distance':round(total,2),'battery_required':round(required,2),'feasible':battery>=required}
class SafetyRules:
    def __init__(self,min_return=25,critical=15): self.min_return=min_return; self.critical=critical
    def evaluate(self,t,recommended):
        if t.battery<self.critical:return {'allowed':False,'action':'ABORT','reason':f'Battery {t.battery:.1f}% is below critical threshold.'}
        if not t.communication:return {'allowed':False,'action':'RETURN_HOME','reason':'Communication link is unavailable; failsafe return is required.'}
        if t.battery<self.min_return:return {'allowed':False,'action':'RETURN_HOME','reason':f'Battery {t.battery:.1f}% is below return threshold.'}
        if recommended=='HOLD_FOR_APPROVAL':return {'allowed':False,'action':'HOLD_FOR_APPROVAL','reason':'Critical condition requires human approval.'}
        return {'allowed':True,'action':recommended,'reason':'Hard safety constraints permit the recommended action.'}
HAZARD_BASE={'fire':5,'smoke':4,'person':1,'truck':1,'car':1,'excavation':4,'knife':4,'electrical':4,'construction vehicle':3}
def score_risk(detections):
    labels=[d['label'].lower() for d in detections]; reasons=[]; severity=1
    for label in labels:
        severity=max(severity,HAZARD_BASE.get(label,1))
        if label in ('fire','smoke','excavation','electrical'): reasons.append(f'{label.title()} was directly observed.')
    if 'person' in labels and any(x in labels for x in ('fire','smoke','excavation','electrical')): severity=min(5,severity+1); reasons.append(f'{labels.count("person")} person(s) are visible near a hazard.')
    if len(set(labels))>=4: severity=min(5,severity+1); reasons.append('Multiple object categories increase operational complexity.')
    level=['','Low','Minor','Moderate','High','Critical'][severity]; action='HOLD_FOR_APPROVAL' if severity>=5 else 'REINSPECT' if severity>=4 else 'CONTINUE'
    return {'severity':severity,'risk_level':level,'reasons':reasons or ['No material hazard was directly observed.'],'recommended_action':action}
