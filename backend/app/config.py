import os


def _normalize_llm_base_url(url: str) -> str:
    """Ensure OpenAI-compatible base URL ends with /v1 for /chat/completions."""
    normalized = url.rstrip("/")
    if normalized.endswith("/v1"):
        return normalized
    # PPIO: https://api.ppio.com/openai -> .../openai/v1
    if "ppio.com" in normalized or normalized.endswith("/openai"):
        return f"{normalized}/v1"
    return normalized


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://rednote:rednote@localhost:3306/rednote",
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
_raw_llm_base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_BASE_URL = _normalize_llm_base_url(_raw_llm_base)
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-r1")
IDEATION_LLM_MODEL = os.getenv("IDEATION_LLM_MODEL", "deepseek/deepseek-v3")
IDEATION_LLM_TIMEOUT = float(os.getenv("IDEATION_LLM_TIMEOUT", "90"))
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")

# Image generation
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "auto")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-2")
IMAGE_USE_PLACEHOLDER = os.getenv("IMAGE_USE_PLACEHOLDER", "false")
IMAGE_API_TIMEOUT = float(os.getenv("IMAGE_API_TIMEOUT", "30"))
IMAGE_API_BASE_URL = os.getenv(
    "IMAGE_API_BASE_URL", "https://api.openai.com/v1"
).rstrip("/")
PPIO_API_BASE = os.getenv("PPIO_API_BASE", "https://api.ppio.com").rstrip("/")
PPIO_IMAGE_MODEL = os.getenv("PPIO_IMAGE_MODEL", "seedream-4.0")
PPIO_IMAGE_POLL_INTERVAL = float(os.getenv("PPIO_IMAGE_POLL_INTERVAL", "2.0"))
PPIO_IMAGE_POLL_TIMEOUT = float(os.getenv("PPIO_IMAGE_POLL_TIMEOUT", "120.0"))


def resolve_image_provider() -> str:
    mode = IMAGE_PROVIDER.lower()
    if mode not in ("", "auto"):
        return mode
    if "ppio.com" in _raw_llm_base.lower() or "ppio.com" in LLM_BASE_URL.lower():
        return "ppio"
    return "openai"

_default_cors = "http://localhost:3000"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _default_cors).split(",")
    if origin.strip()
]
