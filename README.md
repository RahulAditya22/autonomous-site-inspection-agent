# AeroGuard

**AI-Assisted Aerial Site Inspection & Automated Incident Response**

AeroGuard turns aerial/site images into structured safety observations and deterministic operational actions. It is intentionally hardware-independent: images can come from a drone, satellite source, inspection archive, or public dataset.

## What it demonstrates

- Computer-vision API integration with Google Gemini
- Image validation and Base64 transport
- Strict structured JSON validation
- Confidence-aware decision making
- Deterministic incident/action policy
- CSV + JSON persistence
- Optional webhook alerting
- Environment-based secret management
- Automated unit tests

## Architecture

```text
Aerial Image
     |
     v
Image Validation
     |
     v
Gemini Vision Adapter
     |
     v
Structured JSON Validation
     |
     v
Incident / Severity Policy
     |------------------|
     v                  v
CSV + JSON Log       Webhook Alert
```

The AI proposes an observation. Python validates the response and makes the operational decision. This separation prevents an LLM response from directly controlling the application.

## Recommended free model

**Google Gemini 2.5 Flash** is the recommended model for this project because it supports image input and structured generation and is practical for a small student project when used within Google's current free-tier limits. Free-tier availability and quotas can change, so check Google's current Gemini API pricing/quota page before use.

## Setup — Windows PowerShell

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Add your API key

Open `.env`. **Fill the blank value on line 2:**

```text
GEMINI_API_KEY=""
```

Replace only the empty quotes with your Gemini API key. Do not commit `.env` to GitHub; it is ignored by `.gitignore`.

Optional webhook: fill `ALERT_WEBHOOK_URL` on line 5 if you want alerts. It may remain blank.

## Run

Put an aerial image anywhere on your machine and run:

```powershell
$env:PYTHONPATH="backend"
python backend/run.py path\to\image.jpg
```

The inspection result is printed to the terminal and saved under `data/output/`.

## Tests

The test suite does not require an API key and does not make network calls:

```powershell
$env:PYTHONPATH="backend"
pytest -q
```

## Output

`data/output/incidents.csv` contains an append-only incident history. `data/output/latest_incident.json` contains the latest result.

## Important limitation

AeroGuard is an AI-assisted inspection/triage tool, not a certified safety system. It does not establish that a person is actually trespassing or that an observed object is dangerous. Real deployment requires validated site-specific datasets, human review, access-control integration, and appropriate safety testing.

## Resume description

> Built an AI-assisted aerial site inspection pipeline using Python and Gemini vision, implementing structured JSON validation, confidence-aware threat classification, deterministic incident-response rules, persistent event logging, optional webhook alerts, environment-based secret management, and automated tests.
