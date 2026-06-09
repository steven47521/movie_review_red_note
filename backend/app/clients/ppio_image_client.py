import time
from pathlib import Path

import httpx

from app.config import (
    OPENAI_API_KEY,
    PPIO_API_BASE,
    PPIO_IMAGE_MODEL,
    PPIO_IMAGE_POLL_INTERVAL,
    PPIO_IMAGE_POLL_TIMEOUT,
)

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "static" / "images"

# Async txt2img endpoints under /v3/async/{name}
PPIO_ASYNC_MODELS = {
    "qwen-image-txt2img",
    "z-image-turbo",
    "hunyuan-image-3",
    "glm-image",
}

# Sync endpoints under /v3/{name}
PPIO_SYNC_MODELS = {
    "seedream-4.0",
    "seedream-4.5",
    "seedream-5.0-lite",
}

TASK_SUCCEEDED = "TASK_STATUS_SUCCEED"
TASK_FAILED = "TASK_STATUS_FAILED"


class PPIOImageClientError(Exception):
    pass


class PPIOImageClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        api_base: str | None = None,
    ):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or PPIO_IMAGE_MODEL
        self.api_base = (api_base or PPIO_API_BASE).rstrip("/")

    def generate(
        self,
        *,
        prompt: str,
        image_type: str,
        session_id: str,
        size: str = "1024x1024",
    ) -> str:
        if not self.api_key:
            raise PPIOImageClientError("OPENAI_API_KEY is not configured")

        if self.model in PPIO_SYNC_MODELS or self.model.startswith("seedream"):
            url = self._generate_sync(prompt=prompt, size=size)
        else:
            url = self._generate_async(prompt=prompt, size=size)

        return self._mirror_remote_url(url, session_id=session_id, image_type=image_type)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _async_size(size: str) -> str:
        return size.lower().replace("x", "*")

    @staticmethod
    def _sync_size(size: str) -> str:
        normalized = size.lower().replace("*", "x")
        if normalized in ("1024x1024", "1k"):
            return "1440x2560"
        return normalized

    def _build_async_payload(self, prompt: str, size: str) -> dict:
        async_size = self._async_size(size)
        if self.model == "z-image-turbo":
            return {"prompt": prompt, "size": async_size, "seed": -1}
        return {"prompt": prompt, "size": async_size, "watermark": False}

    def _build_sync_payload(self, prompt: str, size: str) -> dict:
        return {
            "prompt": prompt,
            "size": self._sync_size(size),
            "sequential_image_generation": "disabled",
            "watermark": False,
        }

    def _generate_async(self, *, prompt: str, size: str) -> str:
        endpoint = f"{self.api_base}/v3/async/{self.model}"
        payload = self._build_async_payload(prompt, size)

        with httpx.Client(timeout=60.0) as client:
            submit = client.post(endpoint, headers=self._headers(), json=payload)
            submit.raise_for_status()
            task_id = submit.json().get("task_id")
            if not task_id:
                raise PPIOImageClientError("PPIO did not return task_id")

            deadline = time.time() + PPIO_IMAGE_POLL_TIMEOUT
            while time.time() < deadline:
                poll = client.get(
                    f"{self.api_base}/v3/async/task-result",
                    headers=self._headers(),
                    params={"task_id": task_id},
                    timeout=30.0,
                )
                poll.raise_for_status()
                data = poll.json()
                status = (data.get("task") or {}).get("status", "")
                if status == TASK_SUCCEEDED:
                    return self._extract_image_url(data)
                if status == TASK_FAILED:
                    reason = (data.get("task") or {}).get("reason") or "unknown error"
                    raise PPIOImageClientError(f"PPIO image task failed: {reason}")
                time.sleep(PPIO_IMAGE_POLL_INTERVAL)

        raise PPIOImageClientError(
            f"PPIO image task timed out after {int(PPIO_IMAGE_POLL_TIMEOUT)}s"
        )

    def _generate_sync(self, *, prompt: str, size: str) -> str:
        endpoint = f"{self.api_base}/v3/{self.model}"
        payload = self._build_sync_payload(prompt, size)

        with httpx.Client(timeout=PPIO_IMAGE_POLL_TIMEOUT) as client:
            resp = client.post(endpoint, headers=self._headers(), json=payload)
            resp.raise_for_status()
            return self._extract_image_url(resp.json())

    @staticmethod
    def _extract_image_url(data: dict | list) -> str:
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                url = first.get("url") or first.get("image_url")
                if url:
                    return url

        if not isinstance(data, dict):
            raise PPIOImageClientError("Unexpected PPIO image response shape")

        for key in ("images", "data", "generated_images"):
            items = data.get(key)
            if not isinstance(items, list) or not items:
                continue
            item = items[0]
            if isinstance(item, str):
                return item
            if isinstance(item, dict):
                url = item.get("url") or item.get("image_url")
                if url:
                    return url

        url = data.get("url") or data.get("image_url")
        if url:
            return url

        raise PPIOImageClientError("No image URL in PPIO response")

    def _mirror_remote_url(
        self, url: str, *, session_id: str, image_type: str
    ) -> str:
        if url.startswith("/static/"):
            return url

        with httpx.Client(timeout=90.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "image/jpeg")
            ext = "jpg"
            if "png" in content_type:
                ext = "png"
            elif "webp" in content_type:
                ext = "webp"

        out_dir = STORAGE_ROOT / session_id
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{image_type}_{int(time.time() * 1000)}.{ext}"
        path = out_dir / filename
        path.write_bytes(resp.content)
        return f"/static/images/{session_id}/{filename}"
