def decide_action(severity):
    if not isinstance(severity, int):
        raise TypeError("Severity must be an integer.")

    if severity < 1 or severity > 5:
        raise ValueError("Severity must be between 1 and 5.")

    if severity <= 2:
        return "log_only"

    if severity <= 4:
        return "send_alert"

    return "flag_for_human_approval"
