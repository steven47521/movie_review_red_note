# 片语 RedNote — 经典电影小红书创作助手

> 输入经典电影片名 → 自动调研主流观点 → 选主题角度与论述路线 → 多元 AI 评审团在 Review Room 迭代改稿 → gpt-image-2 配图 → 一键完成小红书风格图文笔记。

**技术栈：** FastAPI · Next.js 15 · MySQL 8 · OpenAI LLM + gpt-image-2 · [nexu-io/open-design](https://github.com/nexu-io/open-design) Linear 设计系统

**30 秒价值：** 解决「网页端 AI 一次性出影评水文、AI 感重、不够小红书网感」的痛点，用可回放的多阶段流程把质量控住。

## Quick Start

```bash
# Install backend dependencies
make install
# Windows (no make): cd backend && pip install -r requirements.txt

# Run tests
make test
# Windows: cd backend && python -m pytest -v

# Frontend (T10+)
make frontend-install
cd frontend && npm run dev
make frontend-test
# Windows: cd frontend && npm test

# Local dev (Windows, no Docker):
#   1. cp .env.example .env   # fill TMDB_API_KEY / OPENAI_API_KEY
#   2. Terminal A: cd frontend && npm run dev
#   3. Terminal B (project root): .\scripts\start-backend.ps1
#      or from backend/: .\start-backend.ps1
#   4. http://localhost:3000/dashboard?new=1

# Main workspace (Web-Prototype design): http://localhost:3000/dashboard
# New session: http://localhost:3000/dashboard?new=1
# Design source: Web-Prototype/ (Open Design export)

# Docker full stack (T13+)
cp .env.example .env
make docker-build
make docker-up
curl http://localhost:8000/health
# Frontend: http://localhost:3000  Backend API: http://localhost:8000

# Local dev: MySQL only + migrations
make docker-up-db
make migrate
```

## Requirements

- Python 3.12+（CI）；本地开发 3.10+ 可运行 T1 测试
- Node.js 20+（T10 前端）
- Docker & Docker Compose（T13+）

## Environment Variables

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | MySQL connection string |
| `OPENAI_API_KEY` | Yes | OpenAI API key (LLM + gpt-image-2) |
| `TMDB_API_KEY` | Yes | TMDB movie metadata |
| `API_SECRET_KEY` | Yes | Single-user auth key |
| `NEXT_PUBLIC_API_URL` | Frontend | Browser-facing API base URL (default `http://localhost:8000`) |

## Docker

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000/health |
| MySQL | 3306 | `rednote:rednote@localhost:3306/rednote` |

```bash
make docker-build    # build backend + frontend images
make docker-up       # start mysql, backend, frontend
make docker-down     # stop stack
```

GHCR images (on push to `main`): `ghcr.io/<owner>/<repo>/backend` and `ghcr.io/<owner>/<repo>/frontend`

## Production URLs

> 部署完成后将下方占位符替换为真实公网地址（见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)）

| 环境 | URL |
|------|-----|
| Frontend | `https://YOUR-FRONTEND-URL`（Render `rednote-web` 或 Railway frontend） |
| Backend API | `https://YOUR-BACKEND-URL/health`（Render `rednote-api` 或 Railway backend） |

快速验证：

```bash
# Linux/macOS/Git Bash
./scripts/verify-deployment.sh https://YOUR-BACKEND-URL
```

云部署配置：`render.yaml`（Render Blueprint）、`railway.toml`（Railway 参考）、`docs/DEPLOYMENT.md`

## Project Structure

```
AI4SE_Final_Project/
├── backend/              # FastAPI app
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── Web-Prototype/        # Open Design 原型（index.html + DESIGN-HANDOFF）
├── frontend/             # Next.js 15 + Vitest (T10+)
│   ├── src/styles/prototype/   # 从 Web-Prototype 提取的 tokens + workspace CSS
│   ├── src/components/workspace/WorkspaceShell.tsx
│   ├── src/app/dashboard/page.tsx
│   ├── src/components/creation-wizard/
│   ├── src/components/ideation-wizard/
│   ├── src/components/draft-editor/
│   ├── src/components/image-gallery/
│   ├── src/components/review-room/
│   └── tests/
├── claudecode/           # P0-B 冷启动试做（归档，以根目录为准）
├── docker-compose.yml  # mysql + backend + frontend
├── backend/Dockerfile
├── frontend/Dockerfile
├── Makefile
├── SPEC.md  PLAN.md  SPEC_PROCESS.md  AGENT_LOG.md  REFLECTION.md
└── .github/workflows/ci.yml
```

## API

- `GET /health` — liveness probe（见 SPEC.md §7.0）
- `POST /api/v1/sessions` — 创建创作会话（传入片名）
- `POST /api/v1/sessions/{id}/research` — 调研影片并生成主流观点摘要
- `GET /api/v1/sessions/{id}/research` — 获取调研结果
- `POST /api/v1/sessions/{id}/angles/generate` — 生成 3–5 个主题切入点
- `POST /api/v1/sessions/{id}/angles/select` — 选定主题角度
- `POST /api/v1/sessions/{id}/routes/generate` — 生成 2 套论述路线
- `POST /api/v1/sessions/{id}/routes/select` — 选定路线，进入成稿阶段
- `POST /api/v1/sessions/{id}/reviewers/match` — 匹配评审团（成稿前）
- `POST /api/v1/sessions/{id}/draft/generate` — 生成初稿
- `GET /api/v1/sessions/{id}/review/stream?phase=text` — Review Room SSE 聊天流
- `POST /api/v1/sessions/{id}/review/continue` — 继续优化（≤5 轮）
- `POST /api/v1/sessions/{id}/review/finalize-text` — 文案定稿，进入配图
- `POST /api/v1/sessions/{id}/draft/regenerate` — 分段重写（title/hooks/body/tags）
- `POST /api/v1/sessions/{id}/draft/de-ai-polish` — 去 AI 感润色
- `PATCH /api/v1/sessions/{id}/draft` — 手动保存编辑
- `POST /api/v1/sessions/{id}/images/generate` — gpt-image-2 生成封面+内容图（≥3张）
- `GET /api/v1/sessions/{id}/images` — 获取最新配图
- `POST /api/v1/sessions/{id}/images/regenerate` — 单张重生成
- `GET /api/v1/sessions/{id}/review/stream?phase=image` — 配图审稿 SSE
- `POST /api/v1/sessions/{id}/review/continue?phase=image` — 配图审稿下一轮（≤5轮）
- `POST /api/v1/sessions/{id}/review/finalize` — 完成创作
- `GET /api/v1/sessions` — 创作历史列表（`?favorite=&published=&status=&movie_title=`）
- `GET /api/v1/sessions/{id}` — 会话详情
- `GET /api/v1/sessions/{id}/timeline` — 全流程时间线回放
- `PATCH /api/v1/sessions/{id}` — 收藏 / 标记已发布（`is_favorite`, `is_published`）
- `GET /api/v1/personas` — 80 审稿人格库
- `POST /api/v1/sessions/{id}/reviewers/match` — 按电影匹配评审团
- 完整 API：SPEC.md §7

## Docs

| 文件 | 说明 |
|------|------|
| [SPEC.md](SPEC.md) | 产品规约（10 节 + AC1–AC12） |
| [PLAN.md](PLAN.md) | 实现计划（P0–T15 + C1 进度） |
| [SPEC_PROCESS.md](SPEC_PROCESS.md) | Brainstorming + 冷启动验证记录 |
| [AGENT_LOG.md](AGENT_LOG.md) | Superpowers 协作过程日志 |
| [REFLECTION.md](REFLECTION.md) | 期末反思报告（本人撰写，约 2100 字） |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Railway / Render 云部署 |

## Deliverables（AI4SE 期末）

| 交付物 | 状态 |
|--------|------|
| SPEC / PLAN / SPEC_PROCESS | ✅ |
| 源代码 + 测试 | ✅ `pytest` + `vitest`（见 CI） |
| Docker + CI + GHCR | ✅ 见 `.github/workflows/ci.yml` |
| Open Design 前端 | ✅ `frontend/open-design/` |
| AGENT_LOG | ✅ P0-A → T15 逐条记录 |
| REFLECTION | ✅ |
| 演示视频 | [`docs/demo/演示视频提交.mp4`](docs/demo/演示视频提交.mp4)（约 5–10 分钟功能演示） |
| 公网 URL | ⏳ 配置就绪，见 [DEPLOYMENT.md](docs/DEPLOYMENT.md) 部署后填入上表 |

## CI

GitHub Actions 在每次 push 运行：

1. `backend` — `pytest`（Python 3.12）
2. `frontend` — `npm test`（Node 20）
3. `docker` — `docker compose build` + health check `GET /health`
4. `publish`（仅 `main` 分支 push）— 推送镜像至 GHCR
