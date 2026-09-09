# Architecture

Mission Agent → deterministic Planner → `DroneController` → Perception Agent → deterministic Risk Engine → Safety Agent + local RAG → persistent Mission Memory → dashboard.

Agents exchange typed structures and JSON event payloads. Hard constraints are outside the AI layer. `DroneController` is the seam for a future MAVLink/PX4/ArduPilot adapter.
