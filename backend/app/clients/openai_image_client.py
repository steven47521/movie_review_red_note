import base64
import html
import time
from pathlib import Path

import httpx

from app.clients.ppio_image_client import PPIOImageClient, PPIOImageClientError
from app.config import (
    IMAGE_API_BASE_URL,
    IMAGE_API_TIMEOUT,
    IMAGE_MODEL,
    IMAGE_USE_PLACEHOLDER,
    OPENAI_API_KEY,
    resolve_image_provider,
)

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "static" / "images"


class OpenAIImageClientError(Exception):
    pass


def should_use_placeholder() -> bool:
    mode = IMAGE_USE_PLACEHOLDER.lower()
    if mode in ("1", "true", "yes"):
        return True
    if mode in ("0", "false", "no"):
        return False
    return False


class OpenAIImageClient:
    def __init__(self, api_key: str | None = None, model: str = IMAGE_MODEL):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model
        self._provider = resolve_image_provider()
        self._ppio = PPIOImageClient(api_key=self.api_key)

    def generate(
        self,
        *,
        prompt: str,
        image_type: str,
        session_id: str,
        size: str = "1024x1024",
        max_retries: int = 1,
    ) -> str:
        if should_use_placeholder():
            return self._placeholder_url(
                session_id=session_id,
                image_type=image_type,
                prompt=prompt,
            )

        if self._provider == "ppio":
            try:
                return self._ppio.generate(
                    prompt=prompt,
                    image_type=image_type,
                    session_id=session_id,
                    size=size,
                )
            except PPIOImageClientError as exc:
                if IMAGE_USE_PLACEHOLDER.lower() == "auto":
                    return self._placeholder_url(
                        session_id=session_id,
                        image_type=image_type,
                        prompt=prompt,
                    )
                raise OpenAIImageClientError(str(exc)) from exc

        if not self.api_key:
            return self._placeholder_url(
                session_id=session_id,
                image_type=image_type,
                prompt=prompt,
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
        }
        images_url = f"{IMAGE_API_BASE_URL}/images/generations"

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                with httpx.Client(timeout=IMAGE_API_TIMEOUT) as client:
                    resp = client.post(
                        images_url,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json=payload,
                    )
                    resp.raise_for_status()
                    data = resp.json()["data"][0]
                if data.get("url"):
                    return data["url"]
                if data.get("b64_json"):
                    return self._save_b64(
                        data["b64_json"],
                        session_id=session_id,
                        image_type=image_type,
                    )
                raise OpenAIImageClientError("No image data in API response")
            except (httpx.HTTPError, KeyError, IndexError, OpenAIImageClientError) as exc:
                last_error = exc
                if attempt < max_retries:
                    time.sleep(2**attempt)
                continue

        if IMAGE_USE_PLACEHOLDER.lower() == "auto":
            return self._placeholder_url(
                session_id=session_id,
                image_type=image_type,
                prompt=prompt,
            )

        raise OpenAIImageClientError(str(last_error)) from last_error

    def _placeholder_url(
        self, *, session_id: str, image_type: str, prompt: str
    ) -> str:
        out_dir = STORAGE_ROOT / session_id
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{image_type}_placeholder_{int(time.time() * 1000)}.svg"
        path = out_dir / filename

        labels = {
            "cover": "封面",
            "quote_card": "金句卡",
            "mood_shot": "氛围图",
            "theme_visual": "主题视觉",
        }
        label = labels.get(image_type, image_type)
        hint = html.escape(prompt[:72].replace("\n", " "))

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="500" viewBox="0 0 400 500">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#141824"/>
      <stop offset="100%" stop-color="#3d4a7a"/>
    </linearGradient>
  </defs>
  <rect width="400" height="500" fill="url(#bg)"/>
  <text x="200" y="210" fill="#eef2ff" font-family="sans-serif" font-size="24" text-anchor="middle">{label}</text>
  <text x="200" y="260" fill="#94a3b8" font-family="sans-serif" font-size="13" text-anchor="middle">RedNote 占位配图</text>
  <text x="200" y="320" fill="#64748b" font-family="sans-serif" font-size="11" text-anchor="middle">{hint}</text>
</svg>"""
        path.write_text(svg, encoding="utf-8")
        return f"/static/images/{session_id}/{filename}"

    def _save_b64(self, b64_data: str, session_id: str, image_type: str) -> str:
        out_dir = STORAGE_ROOT / session_id
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{image_type}_{int(time.time())}.png"
        path = out_dir / filename
        path.write_bytes(base64.b64decode(b64_data))
        return f"/static/images/{session_id}/{filename}"
