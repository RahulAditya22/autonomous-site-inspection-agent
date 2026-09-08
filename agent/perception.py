import base64
import os

from anthropic import Anthropic
from PIL import Image

from config import ANTHROPIC_API_KEY


client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


def encode_image(image_path):
    with Image.open(image_path) as image:
        image_format = image.format or "JPEG"

    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    media_type = f"image/{image_format.lower()}"

    return image_data, media_type


def mock_analyze_image(image_path):
    with Image.open(image_path) as image:
        width, height = image.size

    return {
        "description": (
            f"Local demo analysis of a {width}x{height} aerial image."
        ),
        "anomalies": [],
        "severity": 1,
        "source": "mock",
    }


def analyze_image(image_path):
    perception_mode = os.getenv("PERCEPTION_MODE", "mock").lower()

    if perception_mode == "mock":
        return mock_analyze_image(image_path)

    if perception_mode != "anthropic":
        raise ValueError(
            "PERCEPTION_MODE must be either 'mock' or 'anthropic'."
        )

    if client is None:
        raise ValueError(
            "ANTHROPIC_API_KEY is required when PERCEPTION_MODE is 'anthropic'."
        )

    image_data, media_type = encode_image(image_path)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Analyze this aerial site inspection image. "
                            "Identify visible anomalies, damage, hazards, "
                            "or unusual conditions. Describe your findings "
                            "clearly and concisely."
                        ),
                    },
                ],
            }
        ],
    )

    return {
        "description": response.content[0].text,
        "anomalies": [],
        "severity": 1,
        "source": "anthropic",
    }
