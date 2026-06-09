from unittest.mock import MagicMock, patch

import pytest

from app.clients.openai_image_client import OpenAIImageClient, should_use_placeholder
from app.clients.ppio_image_client import PPIOImageClient, PPIOImageClientError


def test_should_use_placeholder_only_when_explicit():
    assert should_use_placeholder() is False


def test_ppio_async_generate_polls_until_success(monkeypatch, tmp_path):
    monkeypatch.setattr("app.clients.ppio_image_client.STORAGE_ROOT", tmp_path)

    submit_resp = MagicMock()
    submit_resp.raise_for_status = MagicMock()
    submit_resp.json.return_value = {"task_id": "task-123"}

    pending_resp = MagicMock()
    pending_resp.raise_for_status = MagicMock()
    pending_resp.json.return_value = {
        "task": {"status": "TASK_STATUS_PROCESSING"},
        "images": [],
    }

    done_resp = MagicMock()
    done_resp.raise_for_status = MagicMock()
    done_resp.json.return_value = {
        "task": {"status": "TASK_STATUS_SUCCEED"},
        "images": [{"image_url": "https://cdn.example/output.jpg"}],
    }

    download_resp = MagicMock()
    download_resp.raise_for_status = MagicMock()
    download_resp.headers = {"content-type": "image/jpeg"}
    download_resp.content = b"fake-image-bytes"

    client_mock = MagicMock()
    client_mock.post.return_value = submit_resp
    client_mock.get.side_effect = [pending_resp, done_resp, download_resp]
    client_mock.__enter__ = MagicMock(return_value=client_mock)
    client_mock.__exit__ = MagicMock(return_value=False)

    with patch("app.clients.ppio_image_client.httpx.Client", return_value=client_mock):
        with patch("app.clients.ppio_image_client.time.sleep"):
            client = PPIOImageClient(api_key="sk-test", model="qwen-image-txt2img")
            url = client.generate(
                prompt="电影封面",
                image_type="cover",
                session_id="sess-1",
            )

    assert url.startswith("/static/images/sess-1/cover_")
    assert client_mock.post.call_args[0][0].endswith("/v3/async/qwen-image-txt2img")


def test_ppio_sync_seedream_parses_data_url(monkeypatch, tmp_path):
    monkeypatch.setattr("app.clients.ppio_image_client.STORAGE_ROOT", tmp_path)

    sync_resp = MagicMock()
    sync_resp.raise_for_status = MagicMock()
    sync_resp.json.return_value = {
        "data": [{"url": "https://cdn.example/seedream.jpg"}]
    }

    download_resp = MagicMock()
    download_resp.raise_for_status = MagicMock()
    download_resp.headers = {"content-type": "image/jpeg"}
    download_resp.content = b"seedream"

    client_mock = MagicMock()
    client_mock.post.return_value = sync_resp
    client_mock.get.return_value = download_resp
    client_mock.__enter__ = MagicMock(return_value=client_mock)
    client_mock.__exit__ = MagicMock(return_value=False)

    with patch("app.clients.ppio_image_client.httpx.Client", return_value=client_mock):
        client = PPIOImageClient(api_key="sk-test", model="seedream-4.0")
        url = client.generate(
            prompt="cover art",
            image_type="cover",
            session_id="sess-2",
        )

    assert url.startswith("/static/images/sess-2/cover_")


def test_openai_client_routes_to_ppio(monkeypatch, tmp_path):
    monkeypatch.setattr("app.clients.openai_image_client.should_use_placeholder", lambda: False)
    monkeypatch.setattr("app.clients.openai_image_client.resolve_image_provider", lambda: "ppio")

    ppio = MagicMock()
    ppio.generate.return_value = "/static/images/sess-1/cover_1.jpg"

    client = OpenAIImageClient(api_key="sk-test")
    client._ppio = ppio

    url = client.generate(
        prompt="test",
        image_type="cover",
        session_id="sess-1",
    )
    assert url == "/static/images/sess-1/cover_1.jpg"
    ppio.generate.assert_called_once()


def test_ppio_task_failure_raises():
    submit_resp = MagicMock()
    submit_resp.raise_for_status = MagicMock()
    submit_resp.json.return_value = {"task_id": "task-fail"}

    fail_resp = MagicMock()
    fail_resp.raise_for_status = MagicMock()
    fail_resp.json.return_value = {
        "task": {"status": "TASK_STATUS_FAILED", "reason": "quota exceeded"},
        "images": [],
    }

    client_mock = MagicMock()
    client_mock.post.return_value = submit_resp
    client_mock.get.return_value = fail_resp
    client_mock.__enter__ = MagicMock(return_value=client_mock)
    client_mock.__exit__ = MagicMock(return_value=False)

    with patch("app.clients.ppio_image_client.httpx.Client", return_value=client_mock):
        client = PPIOImageClient(api_key="sk-test", model="qwen-image-txt2img")
        with pytest.raises(PPIOImageClientError, match="quota exceeded"):
            client.generate(prompt="x", image_type="cover", session_id="s1")
