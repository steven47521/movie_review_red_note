# CI / GHCR 状态核对

> 核对时间：2026-06-12（自动拉取 GitHub Actions API）

## 最近一次 CI（main @ `1b09848`）

| 项 | 结果 |
|----|------|
| Workflow | [CI run #1](https://github.com/steven47521/movie_review_red_note/actions/runs/27418777333) |
| 触发 | push to `main` |
| 总状态 | **success** ✅ |

### Jobs

| Job | 结论 | 说明 |
|-----|------|------|
| `backend-test` | ✅ success | Python 3.12 · `pytest -v` |
| `frontend-test` | ✅ success | Node 20 · `npm test` |
| `docker` | ✅ success | `docker compose build` + `curl /health` |
| `publish` | ✅ success | 推送镜像至 GHCR |

## GHCR 镜像地址

CI `publish` job 已成功 login 并 push（见 run #1 job `publish` 日志）。

| 镜像 | 拉取命令 |
|------|----------|
| Backend | `docker pull ghcr.io/steven47521/movie_review_red_note/backend:latest` |
| Frontend | `docker pull ghcr.io/steven47521/movie_review_red_note/frontend:latest` |

GitHub Packages 页面（需登录 GitHub 查看）：

- https://github.com/steven47521/movie_review_red_note/pkgs/container/backend
- https://github.com/steven47521/movie_review_red_note/pkgs/container/frontend

若 Packages 页 404，请在 GitHub → Package settings → **Change visibility → Public**。

## 本地复验

```powershell
cd f:\project\AI4SE_Final_Project
cd backend && python -m pytest -v
cd ..\frontend && npm test
```

## 推送后自动 CI

每次 push 到任意分支触发 test；push 到 `main` 额外触发 GHCR publish（见 `.github/workflows/ci.yml`）。
