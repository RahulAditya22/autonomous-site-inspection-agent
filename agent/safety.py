def check_safety(severity, action):
    if not isinstance(severity, int):
        raise TypeError("Severity must be an integer.")

    if severity < 1 or severity > 5:
        raise ValueError("Severity must be between 1 and 5.")

    if not action:
        raise ValueError("Action is required.")

    if severity == 5:
        return {
            "approved": False,
            "requires_human": True,
            "reason": "High-severity action requires human approval.",
        }

    return {
        "approved": True,
        "requires_human": False,
        "reason": "Action is within the autonomous safety limit.",
    }
