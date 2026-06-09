from unittest.mock import MagicMock, patch

import httpx

from app.llm.client import LLMClient, _structured_outputs_unsupported


def test_structured_outputs_unsupported_detects_ppio_error():
    response = MagicMock()
    response.status_code = 400
    response.text = (
        '{"message":"model does not support feature: structured-outputs"}'
    )
    assert _structured_outputs_unsupported(response) is True


def test_complete_json_retries_without_structured_outputs():
    client = LLMClient(api_key="test-key", base_url="https://api.example.com/v1")

    fail_resp = MagicMock()
    fail_resp.status_code = 400
    fail_resp.text = "structured-outputs not supported"
    fail_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "bad", request=MagicMock(), response=fail_resp
    )

    ok_resp = MagicMock()
    ok_resp.status_code = 200
    ok_resp.json.return_value = {
        "choices": [{"message": {"content": '{"angles": [{"id": "a1"}]}'}}]
    }
    ok_resp.raise_for_status = MagicMock()

    with patch("app.llm.client.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.side_effect = [fail_resp, ok_resp]
        mock_client_cls.return_value = mock_client

        data = client.complete_json("sys", "user")

    assert data["angles"][0]["id"] == "a1"
    assert mock_client.post.call_count == 2
    assert "response_format" not in mock_client.post.call_args_list[1].kwargs["json"]
