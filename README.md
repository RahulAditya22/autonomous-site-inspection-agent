# AeroGuard

**AI-Assisted Aerial Site Inspection & Automated Incident Response**

AeroGuard turns aerial/site images into structured safety observations and deterministic operational actions. It is hardware-independent: images can come from a drone, satellite source, inspection archive, or public dataset.

## What it demonstrates

- Multimodal AI / computer-vision API integration
- Image validation and Base64 transport
- Strict structured JSON validation
- Confidence-aware decision making
- Deterministic incident/action policy
- CSV + JSON persistence
- Optional webhook alerting
- Environment-based secret management
- Automated unit tests and GitHub Actions CI

## Architecture

```text
Aerial Image -> Image Validation -> Gemini Vision -> JSON Validation
                                      |
                                      v
                         Incident / Severity Policy
                              /                 \
                       CSV + JSON           Webhook Alert
```

The AI proposes an observation. Python validates the response and makes the operational decision. The model never directly controls the action layer.

## Recommended free model

**Gemini 3.7 Flash** is the current recommendation for this project. Google's documentation describes it as natively multimodal with image input and structured-output support, and Google's current pricing page lists a free tier for Gemini 3.7 Flash. Free-tier quotas and availability can change, so verify the current limits before heavy use. citeturn1search2turn0search0

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

The result is printed to the terminal and saved under `data/output/`.

## Tests

The test suite does not require an API key and makes no network calls:

```powershell
pytest -q
```

GitHub Actions runs the same test suite on pushes and pull requests.

## Output

- `data/output/incidents.csv` — append-only incident history
- `data/output/latest_incident.json` — latest structured result

## Dataset strategy

Use real public aerial imagery for demonstrations, such as VisDrone or another appropriately licensed aerial dataset. The project does not pretend that a generic vision model is a certified construction-safety detector. Site-specific hazard detection should be evaluated with site-specific labelled data before any real deployment claim.

## Important limitation

AeroGuard is an AI-assisted inspection/triage tool, not a certified safety system. It does not establish that a person is actually trespassing or that an observed object is dangerous. Real deployment requires validated datasets, human review, access-control integration, and appropriate safety testing.

## Resume description

> Built an AI-assisted aerial site inspection pipeline using Python and Gemini multimodal AI, implementing structured JSON validation, confidence-aware threat classification, deterministic incident-response rules, persistent event logging, optional webhook alerts, environment-based secret management, and automated CI tests.
