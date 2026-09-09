from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
@dataclass
class Telemetry:
    drone_id:str; x:float; y:float; altitude:float; speed:float; battery:float; status:str; communication:bool; camera_status:str; health:str; current_task:str|None; mission_status:str
class DroneController(ABC):
    @abstractmethod
    def takeoff(self): ...
    @abstractmethod
    def goto_waypoint(self,x:float,y:float): ...
    @abstractmethod
    def capture_image(self,task_id:str): ...
    @abstractmethod
    def return_to_home(self): ...
    @abstractmethod
    def get_telemetry(self)->Telemetry: ...
    @abstractmethod
    def abort_mission(self): ...
class SimulatedDroneController(DroneController):
    def __init__(self,drone_id,battery=85,speed=12):
        self.telemetry=Telemetry(drone_id,0,0,0,speed,battery,'idle',True,'ready','nominal',None,'idle'); self.home=(0,0); self.faults={'battery_drain':0,'communication_loss':False,'drone_unavailable':False,'camera_failure':False}
    def takeoff(self): self.telemetry.altitude=20; self.telemetry.status='flying'; self.telemetry.mission_status='active'
    def goto_waypoint(self,x,y):
        if not self.telemetry.communication: raise RuntimeError('communication_lost')
        if self.faults['drone_unavailable']: raise RuntimeError('drone_unavailable')
        d=math.hypot(x-self.telemetry.x,y-self.telemetry.y); self.telemetry.x,self.telemetry.y=x,y; self.telemetry.battery=max(0,self.telemetry.battery-d*0.45-self.faults['battery_drain'])
    def capture_image(self,task_id):
        if self.faults['camera_failure'] or self.telemetry.camera_status!='ready': raise RuntimeError('camera_failure')
        return task_id
    def return_to_home(self): self.goto_waypoint(*self.home); self.telemetry.altitude=0; self.telemetry.status='returning'; self.telemetry.mission_status='returning'
    def get_telemetry(self): return self.telemetry
    def abort_mission(self): self.telemetry.status='aborted'; self.telemetry.mission_status='aborted'
