from pathlib import Path

from app.services.actions import save_incident


def test_save_incident(tmp_path: Path):
    result = {
        "threat_detected": True,
        "threat_type": "obstruction",
        "severity": "medium",
        "confidence": 0.8,
        "description": "Obstruction observed",
        "recommended_action": "Inspect area",
        "image_name": "site.jpg",
        "inspected_at": "2026-01-01T00:00:00+00:00",
    }
    path = save_incident(result, tmp_path)
    assert path.exists()
    assert "Obstruction observed" in path.read_text(encoding="utf-8")
    assert (tmp_path / "latest_incident.json").exists()
