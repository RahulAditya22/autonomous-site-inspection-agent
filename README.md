# AegisFleet

**AI Drone Mission Planner & Autonomous Inspection Simulator**

AegisFleet is a local-first agentic inspection platform for demonstrating autonomous mission planning, simulated UAV execution, pixel-based perception, deterministic risk scoring, RAG, persistent mission memory, safety gates, replanning, and operational observability.

## Architecture

Mission Agent → Planning Agent → `DroneController` → Perception Agent → Risk Engine → Safety Agent + RAG → Mission Memory → Dashboard.

Deterministic calculations handle distance, battery, feasibility and safety. No paid API is required. The simulated controller is the hardware seam for a future MAVLink/PX4/ArduPilot adapter.

## Local setup — Windows PowerShell

```powershell
cd aegisfleet
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
copy .env.example .env
python scripts\setup.py
cd frontend
npm install
```

Start backend from the repository root:

```powershell
python backend\run.py
```

In a second terminal:

```powershell
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

## Demo

Click **Run deterministic demo**. The real API creates a mission, the simulator moves D-01, image pixels pass through the local detector, events are persisted, risk/safety rules execute, and battery degradation after the second waypoint forces a feasibility check and return-home replan.

If the optional YOLO weights are unavailable, the perception component explicitly reports that visual claims are unavailable; it never fabricates detections.

## AI and data policy

The application uses a lightweight YOLO11n model pretrained on COCO for general object detection. COCO is not bundled. Site-specific hazards such as smoke, fire, structural anomalies, PPE compliance and trenches require an appropriately licensed and evaluated dataset/model before being claimed as detected. See `docs/dataset.md`.

The local RAG corpus in `data/knowledge/` contains operating, site-safety, emergency and inspection procedures. Mission history is stored in SQLite and searchable through `/api/memory/query`.

## Safety

Severity is deterministic. Battery and communication hard constraints can override agent recommendations. Critical observations require a human approval gate. LLMs cannot bypass these constraints.

## Tests

Backend: `pytest`

Frontend: `cd frontend; npm test`

A local offline environment was used to run the framework-independent backend unit/integration contract tests: **9 passed**. Full Flask API and frontend execution require installing their declared dependencies; this build environment had no package-index network access, so those dependency-backed suites were not falsely reported as executed.

## API

See `docs/api.md`. Important routes include missions, telemetry, demo execution, safety approval, RAG retrieval, memory queries, reports and image analysis.

## Limitations

This is not aerodynamic simulation or flight-control validation. YOLO11n/COCO is not a certified construction inspection model. The demo fixtures are pipeline fixtures, not model benchmark evidence.
