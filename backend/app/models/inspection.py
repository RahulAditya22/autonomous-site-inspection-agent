"""Core inspection data structures and deterministic response validation."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

ALLOWED_SEVERITIES = {"none", "low", "medium", "high", "critical"}
ALLOWED_THREATS = {
    "none",
    "person_in_restricted_zone",
    "vehicle_in_restricted_zone",
    "unsafe_activity",
    "fire_or_smoke",
    "obstruction",
    "unknown_hazard",
}


@dataclass(frozen=True)
class InspectionResult:
    threat_detected: bool
    threat_type: str
    severity: str
    confidence: float
    description: str
    recommended_action: str
    image_name: str = ""
    inspected_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalise_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    raise ValueError("threat_detected must be a boolean")


def validate_result(data: dict[str, Any]) -> InspectionResult:
    required = {
        "threat_detected", "threat_type", "severity", "confidence",
        "description", "recommended_action",
    }
    missing = required - set(data)
    if missing:
        raise ValueError(f"Missing fields: {', '.join(sorted(missing))}")

    threat = str(data["threat_type"]).strip().lower()
    severity = str(data["severity"]).strip().lower()
    confidence = float(data["confidence"])

    if threat not in ALLOWED_THREATS:
        raise ValueError(f"Unsupported threat_type: {threat}")
    if severity not in ALLOWED_SEVERITIES:
        raise ValueError(f"Unsupported severity: {severity}")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if not str(data["description"]).strip():
        raise ValueError("description cannot be empty")
    if not str(data["recommended_action"]).strip():
        raise ValueError("recommended_action cannot be empty")

    return InspectionResult(
        threat_detected=_normalise_bool(data["threat_detected"]),
        threat_type=threat,
        severity=severity,
        confidence=confidence,
        description=str(data["description"]).strip(),
        recommended_action=str(data["recommended_action"]).strip(),
        image_name=str(data.get("image_name", "")),
        inspected_at=str(data.get("inspected_at", "")) or datetime.now(timezone.utc).isoformat(),
    )
