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

### 必须做（影响评分）

1. **补 PR 工作流证据（最大缺口）**  
   课程要求每个 worktree 对应一个 PR，拒绝单次 commit 交全部代码。  
   现状：6 个 commit 直接推 `main`，没有 PR。  
   **可选补救**（时间紧时）：在 README / AGENT_LOG 里诚实说明「单人开发未严格拆 PR」，并保留现有 commit 时间线；理想做法是用 GitHub 补开若干 PR 描述各阶段（工作量较大）。

2. **确认 CI 绿灯**  
   打开 https://github.com/steven47521/movie_review_red_note/actions  
   确认最近一次 push 的 pytest、vitest、docker job 全部通过。

3. **确认 GHCR 镜像**  
   push 到 `main` 后应有：  
   `ghcr.io/steven47521/movie_review_red_note/backend:latest`  
   `ghcr.io/steven47521/movie_review_red_note/frontend:latest`  
   若 Packages 为空，检查 Actions 里 `publish` job 是否失败。

### 建议做（加分 / 减少助教疑问）

4. **PLAN.md 正文勾选** — 把已完成的 task 从 `- [ ]` 改成 `- [x]`，并补上 commit hash（75a9dc2、4f06986 等）。

5. **SPEC_PROCESS.md 开头** — 第 5 行仍写「P0-B 待补充」，但 §7 已完整；改一行避免矛盾。

6. **作业系统填写**  
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
