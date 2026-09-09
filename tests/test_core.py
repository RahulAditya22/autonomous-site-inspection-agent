import pytest

from app.models.inspection import validate_result
from app.services.actions import decide_action


def valid(**overrides):
    data = {
        "threat_detected": True,
        "threat_type": "person_in_restricted_zone",
        "severity": "high",
        "confidence": 0.91,
        "description": "Person detected in restricted area",
        "recommended_action": "Alert site security",
    }
    data.update(overrides)
    return data


def test_valid_result():
    result = validate_result(valid())
    assert result.threat_detected is True
    assert result.severity == "high"


def test_rejects_missing_field():
    data = valid()
    del data["severity"]
    with pytest.raises(ValueError, match="Missing fields"):
        validate_result(data)


def test_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="between 0 and 1"):
        validate_result(valid(confidence=1.1))


def test_rejects_unknown_threat():
    with pytest.raises(ValueError, match="Unsupported threat_type"):
        validate_result(valid(threat_type="alien"))


def test_low_confidence_requires_review():
    assert decide_action(valid(confidence=0.40)) == "Review manually"


def test_no_threat_requires_no_action_review():
    assert decide_action(valid(threat_detected=False, severity="none")) == "Review manually"


def test_high_confidence_high_severity_alert():
    assert decide_action(valid()) == "Log incident and send security alert"


def test_medium_severity_is_logged():
    assert decide_action(valid(severity="medium")) == "Log incident and flag for review"
