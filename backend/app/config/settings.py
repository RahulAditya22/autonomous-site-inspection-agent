from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / '.env')
@dataclass(frozen=True)
class Settings:
    env: str = os.getenv('AEGIS_ENV', 'local')
    database_url: str = os.getenv('DATABASE_URL', f'sqlite:///{(ROOT / "data" / "aegisfleet.db").as_posix()}')
    host: str = os.getenv('HOST', '127.0.0.1')
    port: int = int(os.getenv('PORT', '5000'))
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    min_return_battery: float = float(os.getenv('MIN_RETURN_BATTERY', '25'))
    critical_battery: float = float(os.getenv('CRITICAL_BATTERY', '15'))
    mission_tick_seconds: float = float(os.getenv('MISSION_TICK_SECONDS', '0.55'))
    max_upload_mb: int = int(os.getenv('MAX_UPLOAD_MB', '8'))
    vision_model: str = os.getenv('VISION_MODEL', 'yolo11n.pt')
    vision_confidence: float = float(os.getenv('VISION_CONFIDENCE', '0.30'))
    rag_top_k: int = int(os.getenv('RAG_TOP_K', '3'))
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
settings = Settings()
