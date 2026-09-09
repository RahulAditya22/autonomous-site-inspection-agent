"""Deterministic incident policy and persistence."""

import csv
import json
from pathlib import Path
from typing import Any

ACTIONS = {
    "none": "No action required",
    "low": "Log observation for routine review",
    "medium": "Log incident and flag for review",
    "high": "Log incident and send security alert",
    "critical": "Log incident and escalate immediately",
}


def decide_action(result: dict[str, Any], confidence_threshold: float = 0.65) -> str:
    if not result["threat_detected"] or result["confidence"] < confidence_threshold:
        return "Review manually"
    return ACTIONS[result["severity"]]


def save_incident(
    result: dict[str, Any], output_dir: Path, confidence_threshold: float = 0.65
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "incidents.csv"
    row = dict(result)
    row["automated_action"] = decide_action(result, confidence_threshold)
    fields = list(row.keys())
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    json_path = output_dir / "latest_incident.json"
    json_path.write_text(json.dumps(row, indent=2), encoding="utf-8")
    return path
