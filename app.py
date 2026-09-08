from agent.alerting import send_alert
from agent.decision import decide_action
from agent.perception import analyze_image
from agent.safety import check_safety


def inspect_site(image_path):
    perception = analyze_image(image_path)

    severity = perception["severity"]
    action = decide_action(severity)
    safety = check_safety(severity, action)

    result = {
        "image_path": image_path,
        "description": perception["description"],
        "anomalies": perception["anomalies"],
        "severity": severity,
        "action": action,
        "safety": safety,
    }

    if action == "send_alert" and safety["approved"]:
        alert_message = (
            f"Site inspection alert: {perception['description']} "
            f"Severity: {severity}."
        )
        result["alert"] = send_alert(alert_message)

    return result
