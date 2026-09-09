"""Optional webhook notifier."""

import requests


def send_alert(message: str, webhook_url: str) -> bool:
    if not webhook_url.strip():
        return False
    response = requests.post(webhook_url, json={"text": message}, timeout=10)
    response.raise_for_status()
    return True
