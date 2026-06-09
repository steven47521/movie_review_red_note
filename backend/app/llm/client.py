import json
import re

import httpx

from app.config import LLM_BASE_URL, LLM_MODEL, OPENAI_API_KEY

LLM_TIMEOUT = 120.0


class LLMClientError(Exception):
    pass


def _parse_json_content(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise LLMClientError("LLM returned non-JSON content") from exc
        return json.loads(match.group())


def _structured_outputs_unsupported(response: httpx.Response) -> bool:
    if response.status_code != 400:
        return False
    text = response.text.lower()
    return "structured-outputs" in text or "structured_outputs" in text


class LLMClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.base_url = (base_url or LLM_BASE_URL).rstrip("/")

    def _post_chat(
        self,
        *,
        model: str,
        system: str,
        user: str,
        temperature: float,
        json_mode: bool,
        timeout: float = LLM_TIMEOUT,
    ) -> str:
        payload: dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            if json_mode and _structured_outputs_unsupported(resp):
                return self._post_chat(
                    model=model,
                    system=system,
                    user=user,
                    temperature=temperature,
                    json_mode=False,
                    timeout=timeout,
                )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    def complete_json(
        self,
        system: str,
        user: str,
        model: str | None = None,
        temperature: float = 0.5,
        timeout: float | None = None,
    ) -> dict:
        if not self.api_key:
            raise LLMClientError("OPENAI_API_KEY is not configured")

        model = model or LLM_MODEL
        request_timeout = timeout if timeout is not None else LLM_TIMEOUT
        try:
            content = self._post_chat(
                model=model,
                system=system,
                user=user,
                temperature=temperature,
                json_mode=True,
                timeout=request_timeout,
            )
        except httpx.HTTPStatusError as exc:
            raise LLMClientError(
                f"LLM request failed ({exc.response.status_code}): {exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMClientError(f"LLM request failed: {exc}") from exc

        return _parse_json_content(content)

    def complete_text(
        self,
        system: str,
        user: str,
        model: str | None = None,
        temperature: float = 0.5,
    ) -> str:
        if not self.api_key:
            raise LLMClientError("OPENAI_API_KEY is not configured")

        model = model or LLM_MODEL
        try:
            return self._post_chat(
                model=model,
                system=system,
                user=user,
                temperature=temperature,
                json_mode=False,
            )
        except httpx.HTTPStatusError as exc:
            raise LLMClientError(
                f"LLM request failed ({exc.response.status_code}): {exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMClientError(f"LLM request failed: {exc}") from exc
