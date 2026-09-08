import requests

from config import SLACK_WEBHOOK_URL


def send_alert(message):
    if not message:
        raise ValueError("Alert message is required.")

    if not SLACK_WEBHOOK_URL:
        return {
            "sent": False,
            "reason": "SLACK_WEBHOOK_URL is not configured.",
        }

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10,
    )

    response.raise_for_status()

    return {
        "sent": True,
        "reason": "Alert sent successfully.",
    }
