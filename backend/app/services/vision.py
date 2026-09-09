"""Gemini vision adapter. The rest of the application is provider-independent."""

import base64
import json
import mimetypes

import requests
from PIL import Image

from app.config.settings import settings
from app.models.inspection import validate_result

PROMPT = """
You are an aerial site safety inspection assistant. Inspect the supplied image conservatively.
Return ONLY valid JSON with exactly these fields:
{
  "threat_detected": boolean,
  "threat_type": "none|person_in_restricted_zone|vehicle_in_restricted_zone|unsafe_activity|fire_or_smoke|obstruction|unknown_hazard",
  "severity": "none|low|medium|high|critical",
  "confidence": number between 0 and 1,
  "description": "short factual description",
  "recommended_action": "short operational recommendation"
}
Do not claim that an object is dangerous unless the image provides evidence. If uncertain, use
unknown_hazard with lower confidence. This is decision support, not a final safety determination.
""".strip()


class GeminiVisionClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = (api_key if api_key is not None else settings.gemini_api_key).strip()
        self.model = model or settings.gemini_model

    def inspect(self, image_path: str) -> dict:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is blank. Add your key to .env before API inspection.")

        image_path_obj = Image.open(image_path)
        image_path_obj.verify()
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise ValueError("Supported image types are JPEG, PNG, and WebP")

        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("ascii")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload = {
            "contents": [{"parts": [
                {"text": PROMPT},
                {"inline_data": {"mime_type": mime_type, "data": encoded}},
            ]}],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"},
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        body = response.json()
        try:
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Gemini returned an invalid inspection response") from exc
        return validate_result(parsed).to_dict()
