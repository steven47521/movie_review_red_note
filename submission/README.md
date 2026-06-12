# AI4SE 期末 — 提交材料包

> 项目：**片语 RedNote**（经典电影小红书创作助手）  
> GitHub：https://github.com/steven47521/movie_review_red_note  
> 更新：2026-06-12

本文件夹集中存放课程要交的文档与说明。**正式提交**：作业系统填 **GitHub 仓库链接**。

---

## 文件夹说明

| 目录 | 内容 |
|------|------|
| `01-规约文档/` | SPEC.md、PLAN.md |
| `02-过程记录/` | SPEC_PROCESS.md、AGENT_LOG.md、claude_log.md |
| `03-反思报告/` | REFLECTION.md |
| `04-项目说明/` | 项目 README.md |
| `05-演示视频/` | 演示视频说明.txt（视频在仓库 `docs/demo/`） |
| `06-部署与提交/` | DEPLOYMENT、CI、PR 列表、提交链接 |

源码、Docker、CI 在 GitHub 仓库内，不必重复打包。

---

## 课程要求对照（当前状态）

| 要求 | 状态 | 证据 |
|------|------|------|
| SPEC / PLAN / SPEC_PROCESS | ✅ | `01-规约文档/`、`02-过程记录/` |
| AGENT_LOG + REFLECTION | ✅ | `02-过程记录/`、`03-反思报告/` |
| 源代码 + 测试 | ✅ | 仓库 `backend/`、`frontend/` |
| Docker + CI + GHCR | ✅ | `06-部署与提交/CI_STATUS.md` |
| **18 条 Closed PR + subagent 标注** | ✅ | `06-部署与提交/PR列表.md` |
| PLAN 勾选 + commit hash | ✅ | `01-规约文档/PLAN.md` |
| 演示视频 | ✅ | 仓库 `docs/demo/演示视频提交.mp4` |
| 公网部署 URL | ⏳ 可选 | README 占位符，见 DEPLOYMENT.md |

---

## 关键链接

| 项 | URL |
|----|-----|
| 仓库 | https://github.com/steven47521/movie_review_red_note |
| Closed PR（18 条） | https://github.com/steven47521/movie_review_red_note/pulls?q=is%3Apr+is%3Aclosed |
| CI Actions | https://github.com/steven47521/movie_review_red_note/actions |
| 演示视频 | https://github.com/steven47521/movie_review_red_note/blob/main/docs/demo/演示视频提交.mp4 |
| GHCR backend | `ghcr.io/steven47521/movie_review_red_note/backend:latest` |
| GHCR frontend | `ghcr.io/steven47521/movie_review_red_note/frontend:latest` |

---

## 作业系统填写示例

```
GitHub 仓库：https://github.com/steven47521/movie_review_red_note
演示视频：仓库内 docs/demo/演示视频提交.mp4
PR 工作流：18 条 Closed PR（见 06-部署与提交/PR列表.md）
```
