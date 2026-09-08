from agent.decision import decide_action
from agent.safety import check_safety


def test_low_severity_logs_only():
    action = decide_action(1)

    assert action == "log_only"


def test_medium_severity_sends_alert():
    action = decide_action(3)
    safety = check_safety(3, action)

    assert action == "send_alert"
    assert safety["approved"] is True
    assert safety["requires_human"] is False


def test_high_severity_requires_human():
    action = decide_action(5)
    safety = check_safety(5, action)

    assert action == "flag_for_human_approval"
    assert safety["approved"] is False
    assert safety["requires_human"] is True
