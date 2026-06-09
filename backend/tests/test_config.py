from app.config import _normalize_llm_base_url


def test_normalize_ppio_base_url_adds_v1():
    assert (
        _normalize_llm_base_url("https://api.ppio.com/openai")
        == "https://api.ppio.com/openai/v1"
    )


def test_normalize_openai_base_url_unchanged():
    assert (
        _normalize_llm_base_url("https://api.openai.com/v1")
        == "https://api.openai.com/v1"
    )
