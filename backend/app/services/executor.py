from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw

from app.agents.mission import MissionAgent
from app.agents.planner import PlanningAgent
from app.agents.perception import PerceptionAgent
from app.agents.safety_agent import SafetyAgent
from app.models.db import Drone, Inspection, Mission, SessionLocal, Task
from app.rag.store import RAGStore
from app.scoring.risk import score
from app.services.memory import MissionMemory
from app.services.reports import build_report
from app.simulator.controller import SimulatedDroneController

ROOT = Path(__file__).resolve().parents[3]
DEMO_DIR = ROOT / "data" / "demo"


class MissionExecutor:
    def __init__(self):
        self.agent = MissionAgent()
        self.planner = PlanningAgent()
        self.perception = PerceptionAgent()
        self.rag = RAGStore(ROOT / "data" / "knowledge")
        self.safety = SafetyAgent(self.rag)

    def create(self, db, objective, drone_id):
        drone = db.get(Drone, drone_id)
        if not drone or drone.status == "maintenance":
            raise ValueError("Drone unavailable")

        mission = Mission(
            id=f"M-{uuid4().hex[:8].upper()}",
            objective=objective,
            drone_id=drone_id,
            status="planned",
        )
        tasks = self.agent.parse(objective)
        plan = self.planner.plan(tasks, drone.battery, drone.speed)
        mission.route_json = json.dumps(plan["waypoints"])
        db.add(mission)

        for task in plan["tasks"]:
            db.add(
                Task(
                    id=task.task_id,
                    mission_id=mission.id,
                    location=task.location,
                    x=task.x,
                    y=task.y,
                    priority=task.priority,
                    inspection_type=task.inspection_type,
                    status="pending",
                )
            )

        db.commit()
        MissionMemory(db).save_event(
            mission.id,
            "Mission Agent",
            "mission_parsed",
            f"Mission contains {len(tasks)} inspection tasks.",
            {"tasks": [task.model_dump() for task in tasks], "plan": plan},
        )
        return mission

    def _image_for(self, location):
        files = sorted(DEMO_DIR.glob("*.jpg"))
        if not files:
            DEMO_DIR.mkdir(parents=True, exist_ok=True)
            for idx, scene in enumerate(("a", "b", "c"), 1):
                image = Image.new("RGB", (640, 420), "skyblue")
                draw = ImageDraw.Draw(image)
                draw.rectangle((0, 300, 640, 420), fill="gray")
                draw.rectangle((80, 210, 250, 300), fill="white", outline="black", width=3)
                draw.rectangle((360, 220, 520, 300), fill="orange", outline="black", width=3)
                draw.ellipse((270, 250, 320, 300), fill="black")
                if idx == 3:
                    for y in range(100, 220, 22):
                        draw.ellipse((285, y, 320, y + 35), fill="lightgray")
                image.save(DEMO_DIR / f"point_{scene}.jpg", quality=90)
            files = sorted(DEMO_DIR.glob("*.jpg"))

        location = str(location).upper()
        if location.endswith("A"):
            return files[0]
        if location.endswith("B"):
            return files[min(1, len(files) - 1)]
        if location.endswith("C"):
            return files[min(2, len(files) - 1)]
        return files[-1]

    def run(self, mission_id, induce_fault=False):
        db = SessionLocal()
        try:
            mission = db.get(Mission, mission_id)
            if mission is None:
                raise ValueError("Mission not found")
            drone = db.get(Drone, mission.drone_id)
            if drone is None:
                raise ValueError("Drone not found")

            memory = MissionMemory(db)
            controller = SimulatedDroneController(
                drone.id,
                drone.battery,
                drone.speed,
            )
            if induce_fault:
                controller.faults["battery_drain"] = 12

            mission.status = "active"
            mission.started_at = datetime.utcnow()
            drone.status = "active"
            drone.mission_status = "active"
            db.commit()

            memory.save_event(
                mission.id,
                "Planner",
                "mission_started",
                "Mission execution started.",
            )
            controller.takeoff()

            for index, task in enumerate(mission.tasks):
                task.status = "active"
                drone.current_task = task.location
                db.commit()

                try:
                    controller.goto_waypoint(task.x, task.y)
                    telemetry = controller.get_telemetry()
                    drone.x = telemetry.x
                    drone.y = telemetry.y
                    drone.altitude = telemetry.altitude
                    drone.battery = telemetry.battery
                    db.commit()

                    memory.save_event(
                        mission.id,
                        "Planner",
                        "waypoint_reached",
                        f"Arrived at {task.location}.",
                        {
                            "battery": telemetry.battery,
                            "position": [telemetry.x, telemetry.y],
                        },
                    )

                    image = self._image_for(task.location)
                    controller.capture_image(task.id)
                    perception = self.perception.analyze(str(image))
                    risk = score(perception["detections"])
                    safety = self.safety.decide(
                        controller.get_telemetry(),
                        risk["recommended_action"],
                        " ".join(detection["label"] for detection in perception["detections"]),
                    )
                    final_action = safety["gate"]["action"]

                    inspection = Inspection(
                        mission_id=mission.id,
                        task_id=task.id,
                        image_path=str(image.relative_to(ROOT)),
                        detections_json=json.dumps(perception["detections"]),
                        risk_json=json.dumps(risk),
                        decision_json=json.dumps(
                            {
                                "action": final_action,
                                "summary": safety["summary"],
                                "factors": risk["reasons"],
                                "rag_sources": [item["source"] for item in safety["rag"]],
                            }
                        ),
                    )
                    db.add(inspection)

                    memory.save_event(
                        mission.id,
                        "Perception Agent",
                        "perception",
                        f"Observed {len(perception['detections'])} configured objects at {task.location}.",
                        perception,
                    )
                    memory.save_event(
                        mission.id,
                        "Safety Agent",
                        "decision",
                        safety["summary"],
                        {
                            "risk": risk,
                            "decision": final_action,
                            "rag": safety["rag"],
                        },
                    )

                    if final_action == "HOLD_FOR_APPROVAL":
                        mission.status = "awaiting_approval"
                        db.commit()
                        return mission.id

                    if final_action in ("RETURN_HOME", "ABORT"):
                        if final_action == "RETURN_HOME":
                            controller.return_to_home()
                        else:
                            controller.abort_mission()
                        task.status = "skipped"
                        break

                    if final_action == "REINSPECT":
                        memory.save_event(
                            mission.id,
                            "Planner",
                            "replan",
                            "Secondary inspection scheduled because risk or evidence warrants another look.",
                            {"location": task.location},
                        )

                    task.status = "completed"
                    db.commit()

                    if induce_fault and index == 1:
                        controller.telemetry.battery = min(controller.telemetry.battery, 22)
                        drone.battery = controller.telemetry.battery
                        db.commit()
                        replanned = self.planner.replan(
                            list(mission.tasks),
                            (controller.telemetry.x, controller.telemetry.y),
                            controller.telemetry.battery,
                            drone.speed,
                        )
                        memory.save_event(
                            mission.id,
                            "Planner",
                            "replan",
                            "Original route became unsafe after battery degradation; return-to-home path selected.",
                            replanned,
                        )
                        controller.return_to_home()
                        break

                except RuntimeError as exc:
                    reason = str(exc)
                    memory.save_event(
                        mission.id,
                        "Safety Agent",
                        "failure",
                        f"Drone event: {reason}.",
                        {"error": reason},
                    )
                    if reason == "communication_lost":
                        controller.return_to_home()
                    else:
                        controller.abort_mission()
                    break

            telemetry = controller.get_telemetry()
            drone.x = telemetry.x
            drone.y = telemetry.y
            drone.altitude = telemetry.altitude
            drone.battery = telemetry.battery
            mission.status = "aborted" if telemetry.status == "aborted" else "completed"
            mission.completed_at = datetime.utcnow()
            drone.status = "available"
            drone.current_task = None
            drone.mission_status = mission.status
            db.commit()

            mission.final_result = json.dumps(build_report(db, mission))
            db.commit()
            memory.save_event(
                mission.id,
                "System",
                "mission_completed",
                f"Mission completed with status {mission.status}.",
            )
            return mission_id
        finally:
            db.close()
