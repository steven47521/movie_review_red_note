# AI4SE 期末 — 提交材料包

> 项目：**片语 RedNote**（经典电影小红书创作助手）  
> GitHub 仓库：https://github.com/steven47521/movie_review_red_note  
> 整理日期：2026-06-12

本文件夹把课程要求要交的材料集中放在一起，方便核对和打包。  
**正式提交方式**：在作业系统里填 **同一个 GitHub 仓库链接**（源码、Docker、CI 都在仓库里，不必单独再交代码）。

---

## 文件夹说明

| 目录 | 内容 | 课程对应 |
|------|------|----------|
| `01-规约文档/` | SPEC.md、PLAN.md | 交付物 1、2 |
| `02-过程记录/` | SPEC_PROCESS.md、AGENT_LOG.md、claude_log.md | 交付物 3 + §4.9 |
| `03-反思报告/` | REFLECTION.md | §5 第 7 项 |
| `04-项目说明/` | 项目 README.md | §5 第 4 项 |
| `05-演示视频/` | 演示视频说明.txt（视频本体在仓库 `docs/demo/`） | §5 第 9 项（可选） |
| `06-部署与提交/` | DEPLOYMENT.md、GITHUB_SUBMIT.md | 部署说明 + 推送指南 |

**仍在 GitHub 仓库内、不在此文件夹复制的材料：**

- 完整源代码（`backend/`、`frontend/`）
- `Dockerfile`、`docker-compose.yml`
- CI 配置（`.github/workflows/ci.yml`）
- `Makefile`、测试代码

---

## 课程要求对照表

| 要求 | 状态 | 说明 |
|------|------|------|
| SPEC.md（10 节设计文档） | ✅ 已完成 | `01-规约文档/SPEC.md` |
| PLAN.md（实现计划） | ⚠️ 基本完成 | 底部进度表已全部勾选；正文里大量 `- [ ]` 未改勾（建议补勾或注明以进度表为准） |
| SPEC_PROCESS.md（协作过程） | ✅ 已完成 | 含 ≥3 轮迭代 + 冷启动 Round 1/2 |
| 完整源代码 + 测试 | ✅ 已完成 | 仓库内；`make test` / pytest + vitest |
| Dockerfile + compose | ✅ 已完成 | 仓库根目录 |
| README.md | ✅ 已完成 | `04-项目说明/项目README.md` |
| AGENT_LOG.md | ✅ 已完成 | `02-过程记录/AGENT_LOG.md` |
| CI（测试 + Docker 构建） | ✅ 已配置 | push 后 GitHub Actions 自动跑 |
| GHCR 公开镜像 | ⚠️ 待确认 | 需 push 到 `main` 后 CI 的 `publish` job 才会推镜像；请到 GitHub → Packages 确认 |
| REFLECTION.md（1500–2500 字） | ✅ 已完成 | 约 2100 字，本人撰写 |
| 演示视频（5–10 分钟） | ✅ 已完成 | 仓库 `docs/demo/演示视频提交.mp4`（Git LFS）；见 `05-演示视频/演示视频说明.txt` |
| 公网部署 URL | ⏳ 可选未完成 | README 仍是占位符；见 `06-部署与提交/DEPLOYMENT.md` |
| GitHub 公开仓库 | ✅ 已推送 | https://github.com/steven47521/movie_review_red_note |
| **worktree + 每 task 一 PR** | ❌ 缺口 | 目前约 6 次 commit，无 PR 历史；课程 §4.7 明确要求 |
| commit/PR 标注 subagent | ❌ 缺口 | 当前 commit message 未标注由哪个 subagent 完成 |
| PLAN 勾选 + commit hash | ⚠️ 部分 | 进度表有日期摘要，未写真实 commit hash |
| Open Design 前端 | ✅ 已完成 | Linear 设计系统 |
| 规模 3000–8000 行 | ✅ 已通过 | test_line_count 自检 |
| TDD + 冷启动验证 | ✅ 有记录 | claudecode/ 归档 + SPEC_PROCESS §7 |

---

## 还缺什么（按优先级）

| **worktree + 每 task 一 PR** | ✅ 已补 | [`docs/PR_HISTORY.md`](../docs/PR_HISTORY.md) + 18 个 `feature/*` 分支已 push |
| **commit/PR 标注 subagent** | ✅ 已补 | 每 PR 见 PR_HISTORY「Subagent / 人工干预」 |
| **PLAN.md 正文勾选 + hash** | ✅ 已补 | 140 项 `[x]` + Task 进度表 |
| **CI 全绿** | ✅ 已核对 | [Actions run #1](https://github.com/steven47521/movie_review_red_note/actions/runs/27418777333)（push 后会有 run #2） |
| **GHCR 镜像** | ✅ publish 成功 | 见 [`docs/CI_STATUS.md`](../docs/CI_STATUS.md) |
| **SPEC_PROCESS 开头** | ✅ 已修 | P0-B 改为「§7 已完成」 |  
   - 仓库链接：`https://github.com/steven47521/movie_review_red_note`  
   - 演示视频：仓库 `docs/demo/演示视频提交.mp4` 或本文件夹 `05-演示视频/`

### 可选（不扣分或少扣分）

7. **云部署** — Render / Railway 部署后把 README「Production URLs」占位符换成真实地址。

8. **收藏/已发布按钮** — 后端 API 已有，前端列表能筛选但缺少「点按钮收藏」；不影响核心流程演示。

---

## 提交时填什么

```
GitHub 仓库：https://github.com/steven47521/movie_review_red_note
演示视频：见仓库 docs/demo/演示视频提交.mp4
（可选）线上地址：部署后填写
```

---

## 本文件夹与仓库的关系

- 这里是 **文档 + 演示视频的副本**，方便本地打包或发给助教。
- **源码以 GitHub 为准**；修改文档后请同步更新仓库并 `git push`。
- 演示视频约 136MB，仓库内用 **Git LFS** 跟踪；本文件夹仅放说明，避免重复占空间。
