"""Command-line entry point for one-image inspection."""

import argparse
import json
from pathlib import Path

from app.config.settings import settings
from app.services.actions import decide_action, save_incident
from app.services.alerts import send_alert
from app.services.vision import GeminiVisionClient


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect an aerial site image with Gemini.")
    parser.add_argument("image", type=Path, help="Path to an aerial image")
    args = parser.parse_args()

    if not args.image.is_file():
        parser.error(f"Image not found: {args.image}")

    result = GeminiVisionClient().inspect(str(args.image))
    result["image_name"] = args.image.name
    action = decide_action(result, settings.confidence_threshold)
    result["automated_action"] = action
    save_incident(result, Path("data/output"), settings.confidence_threshold)

    if result["threat_detected"] and result["confidence"] >= settings.confidence_threshold:
        message = f"AeroGuard {result['severity'].upper()} incident: {result['description']}"
        send_alert(message, settings.alert_webhook_url)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
