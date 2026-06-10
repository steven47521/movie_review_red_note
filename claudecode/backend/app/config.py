import os

# All sensitive values must be loaded from environment variables — never hardcoded.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
