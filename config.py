import os

from dotenv import load_dotenv


load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
PERCEPTION_MODE = os.getenv("PERCEPTION_MODE", "mock").lower()


if PERCEPTION_MODE not in ("mock", "anthropic"):
    raise ValueError(
        'PERCEPTION_MODE must be either "mock" or "anthropic".'
    )


if PERCEPTION_MODE == "anthropic" and not ANTHROPIC_API_KEY:
    raise ValueError(
        'ANTHROPIC_API_KEY is required when PERCEPTION_MODE is "anthropic".'
    )
