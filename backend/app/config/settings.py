"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    alert_webhook_url: str = os.getenv("ALERT_WEBHOOK_URL", "").strip()
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))


settings = Settings()
