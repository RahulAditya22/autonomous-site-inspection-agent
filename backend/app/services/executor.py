from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from app.models.db import Mission,Task,Inspection,Drone,SessionLocal
from app.simulator.controller import SimulatedDroneController
from app.agents.mission import MissionAgent
from app.agents.planner import PlanningAgent
from app.agents.perception import PerceptionAgent
from app.agents.safety_agent import SafetyAgent
from app.rag.store import RAGStore
from app.scoring.risk import score
from app.services.memory import MissionMemory
from app.services.reports import build_report
ROOT=Path(__file__).resolve().parents[3]; DEMO_DIR=ROOT/'data'/'demo'
class MissionExecutor:
    def __init__(self): self.agent=MissionAgent(); self.planner=PlanningAgent(); self.perception=PerceptionAgent(); self.rag=RAGStore(ROOT/'data'/'knowledge'); self.safety=SafetyAgent(self.rag)
    def create(self,db,objective,drone_id):
        drone=db.get(Drone,drone_id)
        if not drone or drone.status=='maintenance':raise ValueError('Drone unavailable')
        mission=Mission(id=f'M-{uuid4().hex[:8].upper()}',objective=objective,drone_id=drone_id,status='planned'); tasks=self.agent.parse(objective); plan=self.planner.plan(tasks,drone.battery,drone.speed); mission.route_json=json.dumps(plan['waypoints']); db.add(mission)
        for t in plan['tasks']:db.add(Task(id=t.task_id,mission_id=mission.id,location=t.location,x=t.x,y=t.y,priority=t.priority,inspection_type=t.inspection_type,status='pending'))
        db.commit(); MissionMemory(db).save_event(mission.id,'Mission Agent','mission_parsed',f'Mission contains {len(tasks)} inspection tasks.',{'tasks':[t.model_dump() for t in tasks],'plan':plan}); return mission
    def _image_for(self,location):
        files=sorted(DEMO_DIR.glob('*.jpg'))
        if not files:
            DEMO_DIR.mkdir(parents=True,exist_ok=True); from PIL import Image,ImageDraw
            for idx,scene in enumerate(['a','b','c'],1):
                im=Image.new('RGB',(640,420),'skyblue'); d=ImageDraw.Draw(im); d.rectangle((0,300,640,420),fill='gray'); d.rectangle((80,210,250,300),fill='white',outline='black',width=3); d.rectangle((360,220,520,300),fill='orange',outline='black',width=3); d.ellipse((270,250,320,300),fill='black')
                if idx==3:
                    for y in range(100,220,22):d.ellipse((285,y,320,y+35),fill='lightgray')
                im.save(DEMO_DIR/f'point_{scene}.jpg',quality=90)
            files=sorted(DEMO_DIR.glob('*.jpg'))
        if str(location).upper().endswith('A'):return files[0]
        if str(location).upper().endswith('B'):return files[min(1,len(files)-1)]
        if str(location).upper().endswith('C'):return files[min(2,len(files)-1)]
        return files[-1]
    def run(self,mission_id,induce_fault=False):
        db=SessionLocal(); mission=db.get(Mission,mission_id); drone=db.get(Drone,mission.drone_id); memory=MissionMemory(db); controller=SimulatedDroneController(drone.id,drone.battery,drone.speed)
        if induce_fault:controller.faults['battery_drain']=12
        mission.status='active'; mission.started_at=datetime.utcnow(); drone.status='active'; drone.mission_status='active'; db.commit(); memory.save_event(mission.id,'Planner','mission_started','Mission execution started.'); controller.takeoff()
        for index,task in enumerate(mission.tasks):
            task.status='active'; drone.current_task=task.location; db.commit()
            try:
                controller.goto_waypoint(task.x,task.y); tel=controller.get_telemetry(); drone.x,drone.y,drone.altitude,drone.battery=tel.x,tel.y,tel.altitude,tel.battery; db.commit(); memory.save_event(mission.id,'Planner','waypoint_reached',f'Arrived at {task.location}.',{'battery':tel.battery,'position':[tel.x,tel.y]})
                image=self._image_for(task.location); controller.capture_image(task.id); perception=self.perception.analyze(str(image)); risk=score(perception['detections']); safety=self.safety.decide(controller.get_telemetry(),risk['recommended_action'],' '.join(d['label'] for d in perception['detections'])); final_action=safety['gate']['action']
                db.add(Inspection(mission_id=mission.id,task_id=task.id,image_path=str(image.relative_to(ROOT)),detections_json=json.dumps(perception['detections']),risk_json=json.dumps(risk),decision_json=json.dumps({'action':final_action,'summary':safety['summary'],'factors':risk['reasons'],'rag_sources':[p['source'] for p in safety['rag']}]))); memory.save_event(mission.id,'Perception Agent','perception',f'Observed {len(perception["detections"])} configured objects at {task.location}.',perception); memory.save_event(mission.id,'Safety Agent','decision',safety['summary'],{'risk':risk,'decision':final_action,'rag':safety['rag']})
                if final_action=='HOLD_FOR_APPROVAL':mission.status='awaiting_approval'; db.commit(); return mission.id
                if final_action in ('RETURN_HOME','ABORT'):controller.return_to_home() if final_action=='RETURN_HOME' else controller.abort_mission(); task.status='skipped'; break
                if final_action=='REINSPECT':memory.save_event(mission.id,'Planner','replan','Secondary inspection scheduled because risk or evidence warrants another look.',{'location':task.location})
                task.status='completed'; db.commit()
                if induce_fault and index==1:
                    controller.telemetry.battery=min(controller.telemetry.battery,22); drone.battery=controller.telemetry.battery; db.commit(); replanned=self.planner.replan(list(mission.tasks),(controller.telemetry.x,controller.telemetry.y),controller.telemetry.battery,drone.speed); memory.save_event(mission.id,'Planner','replan','Original route became unsafe after battery degradation; return-to-home path selected.',replanned); controller.return_to_home(); break
            except RuntimeError as exc:
                reason=str(exc); memory.save_event(mission.id,'Safety Agent','failure',f'Drone event: {reason}.',{'error':reason}); controller.return_to_home() if reason=='communication_lost' else controller.abort_mission(); break
        tel=controller.get_telemetry(); drone.x,drone.y,drone.altitude,drone.battery=tel.x,tel.y,tel.altitude,tel.battery; mission.status='aborted' if controller.telemetry.status=='aborted' else 'completed'; mission.completed_at=datetime.utcnow(); drone.status='available'; drone.current_task=None; drone.mission_status=mission.status; db.commit(); mission.final_result=json.dumps(build_report(db,mission)); db.commit(); memory.save_event(mission.id,'System','mission_completed',f'Mission completed with status {mission.status}.'); db.close(); return mission_id
