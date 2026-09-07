import os

from dotenv import load_dotenv


load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set.")
