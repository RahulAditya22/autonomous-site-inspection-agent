# Autonomous Site Inspection Agent

An agent that analyzes aerial imagery, reasons about anomalies, and decides whether to log an inspection, send an alert, or require human approval for high-severity findings.

## Project Architecture

Image Upload
    |
    v
Perception
    |
    v
Severity
    |
    v
Decision
    |
    +------------------+
    |                  |
    v                  v
log_only          send_alert
    |                  |
    |                  v
    |             Slack Alert
    |
    v
Safety Gate
    |
    v
Human Approval Required
for Severity 5

## Tech Stack

- Python
- Flask
- Pillow
- Anthropic Claude API (optional)
- SQLite / SQLAlchemy
- python-dotenv
- Requests
- Pytest
- Git / GitHub

## Decision Rules

| Severity | Action |
|---|---|
| 1-2 | log_only |
| 3-4 | send_alert |
| 5 | flag_for_human_approval |

Severity 5 findings cannot be autonomously approved by the safety gate.

## Running the Project

### 1. Activate the virtual environment

PowerShell:

    .\venv\Scripts\Activate.ps1

### 2. Install dependencies

    pip install -r requirements.txt

### 3. Configure environment variables

For the free local demo, use mock perception:

    mock="mock"

Mock mode does not call the Anthropic API and does not require paid API access.

### 4. Run the Flask application

    python app.py

Open http://127.0.0.1:5000 in your browser.

Upload an image and click Inspect Site.

## Anthropic Vision Mode

The project also contains an optional Anthropic vision integration.

Set:

    mock="anthropic"

Then configure ANTHROPIC_API_KEY in your local environment.

This mode requires an Anthropic account with available API credits.

## Slack Alerts

Slack alerting is optional.

Configure SLACK_WEBHOOK_URL if you want to send alerts to Slack.

If no Slack webhook is configured, the application safely reports that the alert was not sent.

## Testing

Run:

    pytest

The automated test suite verifies:

- Low-severity log-only decisions
- Medium-severity alert decisions
- High-severity human-approval decisions

## Safety

The agent does not autonomously approve severity 5 findings.

For severity 5, the safety gate returns:

    approved = False
    requires_human = True

This provides a human-in-the-loop safety mechanism for high-impact decisions.

## Project Status

The project is being developed step by step with verification after each stage.

See PROGRESS.md for the current implementation progress.
