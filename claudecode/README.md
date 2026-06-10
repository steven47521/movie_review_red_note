# 片语 RedNote — P0-B 冷启动归档

> **已合并至仓库根目录。** 正式开发请以 `../backend/` 为准。本目录保留 Claude Code 冷启动试做记录。

# ~~片语 RedNote — 经典电影小红书创作助手~~

> FastAPI backend + Next.js frontend + MySQL + gpt-image-2

## Quick Start

```bash
# Install backend dependencies
make install

# Run tests
make test

# Start with Docker Compose (includes MySQL)
docker compose up -d
```

## Requirements

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose

## Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | MySQL connection string |
| `OPENAI_API_KEY` | Yes | OpenAI API key (LLM + gpt-image-2) |
| `TMDB_API_KEY` | Yes | TMDB movie metadata |
| `API_SECRET_KEY` | Yes | Single-user auth key |

## Project Structure

```
claudecode/
├── backend/         # FastAPI app
│   ├── app/
│   │   ├── main.py
│   │   └── config.py
│   ├── tests/
│   └── requirements.txt
├── frontend/        # Next.js 15 (T10+)
├── Makefile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## API

- `GET /health` — liveness probe
- See SPEC.md §7 for full API reference

## Image Model

Visual generation uses **gpt-image-2** (OpenAI Images API). See SPEC.md §3.4.2.

## CI

GitHub Actions runs `pytest` + Docker build on every push. See `.github/workflows/ci.yml`.
