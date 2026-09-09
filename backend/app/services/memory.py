from __future__ import annotations
import json
from sqlalchemy import select
from app.models.db import Mission, MissionEvent
class MissionMemory:
    def __init__(self,db): self.db=db
    def save_event(self,mission_id,agent,event_type,summary,payload=None):
        e=MissionEvent(mission_id=mission_id,agent=agent,event_type=event_type,summary=summary,payload_json=json.dumps(payload or {})); self.db.add(e); self.db.commit(); return e
    def search(self,question):
        tokens=[t for t in question.lower().split() if len(t)>2]; missions=self.db.scalars(select(Mission).order_by(Mission.created_at.desc())).all(); out=[]
        for m in missions:
            hay=f'{m.objective} {m.final_result or ""}'.lower()
            if any(t in hay for t in tokens): out.append({'mission_id':m.id,'objective':m.objective,'created_at':m.created_at.isoformat(),'status':m.status,'final_result':m.final_result})
            if len(out)>=10:break
        return out
    def mission_snapshot(self,mission):
        return {'id':mission.id,'objective':mission.objective,'drone_id':mission.drone_id,'status':mission.status,'created_at':mission.created_at.isoformat(),'started_at':mission.started_at.isoformat() if mission.started_at else None,'completed_at':mission.completed_at.isoformat() if mission.completed_at else None,'tasks':[{'id':t.id,'location':t.location,'x':t.x,'y':t.y,'priority':t.priority,'status':t.status} for t in mission.tasks],'events':[{'timestamp':e.timestamp.isoformat(),'agent':e.agent,'type':e.event_type,'summary':e.summary,'payload':json.loads(e.payload_json)} for e in mission.events],'inspections':[{'id':i.id,'task_id':i.task_id,'image_path':i.image_path,'detections':json.loads(i.detections_json),'risk':json.loads(i.risk_json),'decision':json.loads(i.decision_json)} for i in mission.inspections]}
