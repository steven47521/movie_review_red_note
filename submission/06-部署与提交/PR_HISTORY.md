# PR 工作流记录 — 片语 RedNote

> 课程 §4.7：git worktree + 每 task 一 PR；commit/PR 标注 subagent 与人工修改。  
> 仓库：https://github.com/steven47521/movie_review_red_note

## 说明

实现阶段按 **Superpowers subagent-driven-development** 逐 task 派发（见 [`AGENT_LOG.md`](../AGENT_LOG.md)），每个 task 在独立 **git worktree** 分支开发，完成后两阶段 code review，再 merge 到 `main`。

因单人 + 本地批量 push 时曾合并为少量 commit（`4f06986`、`ef3baeb` 等），**Git 上 merge commit 较粗，但每个 task 的分支名、subagent、人工干预均在下表可追溯**。对应 feature 分支已 push 到 origin（`feature/T1-scaffold` … `feature/T15-integration`）。

Compare 链接格式：`https://github.com/steven47521/movie_review_red_note/compare/{base}...{head}`

**GitHub Closed PR 列表（18 条）：** https://github.com/steven47521/movie_review_red_note/pulls?q=is%3Apr+is%3Aclosed  
本地副本：[`submission/06-部署与提交/PR列表.md`](../submission/06-部署与提交/PR列表.md)

---

## PR 总览

| PR | Task | Worktree 分支 | GitHub | Merge commit | 状态 |
|----|------|---------------|--------|--------------|------|
| #1 | P0-A | `feature/P0-spec-process-v2` | [#18](https://github.com/steven47521/movie_review_red_note/pull/18) | `75a9dc2` | ✅ Closed |
| #2 | P0-B | `feature/P0B-cold-start` | [#1](https://github.com/steven47521/movie_review_red_note/pull/1) | `4f06986` | ✅ Closed |
| #3 | T1 | `feature/T1-scaffold` | [#2](https://github.com/steven47521/movie_review_red_note/pull/2) | `4f06986` | ✅ Closed |
| #4 | T2 | `feature/T2-mysql-models` | [#3](https://github.com/steven47521/movie_review_red_note/pull/3) | `4f06986` | ✅ Closed |
| #5 | T3 | `feature/T3-personas` | [#4](https://github.com/steven47521/movie_review_red_note/pull/4) | `4f06986` | ✅ Closed |
| #6 | T4 | `feature/T4-research` | [#5](https://github.com/steven47521/movie_review_red_note/pull/5) | `4f06986` | ✅ Closed |
| #7 | T5 | `feature/T5-ideation` | [#6](https://github.com/steven47521/movie_review_red_note/pull/6) | `4f06986` | ✅ Closed |
| #8 | T6 | `feature/T6-review-room-text` | [#7](https://github.com/steven47521/movie_review_red_note/pull/7) | `4f06986` | ✅ Closed |
| #9 | T7 | `feature/T7-draft-edit` | [#8](https://github.com/steven47521/movie_review_red_note/pull/8) | `4f06986` | ✅ Closed |
| #10 | T8 | `feature/T8-visual-review` | [#9](https://github.com/steven47521/movie_review_red_note/pull/9) | `4f06986` | ✅ Closed |
| #11 | T9 | `feature/T9-library` | [#10](https://github.com/steven47521/movie_review_red_note/pull/10) | `4f06986` | ✅ Closed |
| #12 | T10 | `feature/T10-frontend-scaffold` | [#11](https://github.com/steven47521/movie_review_red_note/pull/11) | `4f06986` | ✅ Closed |
| #13 | T11 | `feature/T11-review-room-ui` | [#12](https://github.com/steven47521/movie_review_red_note/pull/12) | `4f06986` | ✅ Closed |
| #14 | T12 | `feature/T12-frontend-flows` | [#13](https://github.com/steven47521/movie_review_red_note/pull/13) | `4f06986` | ✅ Closed |
| #15 | T13 | `feature/T13-docker-ci` | [#14](https://github.com/steven47521/movie_review_red_note/pull/14) | `ef3baeb` | ✅ Closed |
| #16 | T14 | `feature/T14-deploy` | [#15](https://github.com/steven47521/movie_review_red_note/pull/15) | `4f06986` | ✅ Closed |
| #17 | T15 | `feature/T15-integration` | [#16](https://github.com/steven47521/movie_review_red_note/pull/16) | `4f06986` | ✅ Closed |
| #18 | C1 | `feature/C1-delivery` | [#17](https://github.com/steven47521/movie_review_red_note/pull/17) | `79444e4` | ✅ Closed |

¹ T1–T12、T14–T15 在同一次 worktree 合并中进入 `main`（commit `4f06986`）；各 task 在 worktree 内独立 TDD 完成，合并前均通过 `pytest` / `vitest` checkpoint。详见 [`AGENT_LOG.md`](../AGENT_LOG.md) 各 task 条目。

---

## 各 PR 详情（subagent + 人工干预）

### PR #1 — P0-A: SPEC_PROCESS + 规约文档

- **Subagent**: Cursor + Superpowers `brainstorming` / `writing-plans`
- **人工干预**: 产品方向从 RAG 知识库改为「小红书影评创作」；签字确认 SPEC 10 节
- **验证**: SPEC_PROCESS ≥3 轮迭代；REFLECTION 骨架
- **Compare**: [75a9dc2](https://github.com/steven47521/movie_review_red_note/commit/75a9dc2)

### PR #2 — P0-B: 冷启动验证

- **Subagent**: Codex（Round 1 门禁停问）+ Claude Code（Round 2 T1 TDD）
- **人工干预**: 修订 PLAN 冷启动授权表；合并 `claudecode/` 归档
- **验证**: SPEC_PROCESS §7；`pytest 1 passed` @ claudecode/
- **Compare**: [75a9dc2...4f06986](https://github.com/steven47521/movie_review_red_note/compare/75a9dc2...4f06986)（含 P0-B 归档目录）

### PR #3 — T1: 项目骨架

- **Subagent**: Cursor `subagent-driven-development`
- **人工干预**: 合并 claudecode/ 至根目录；移除 T1 过早 docker-build（D5）；config 默认 MySQL（D6）
- **验证**: `pytest test_health` PASS；`make test` / Windows 等价命令
- **Worktree**: `feature/T1-scaffold`

### PR #4 — T2: MySQL + Alembic

- **Subagent**: Cursor subagent + `test-driven-development`
- **人工干预**: 无
- **验证**: `test_models` PASS；`docker-compose` mysql healthcheck
- **Worktree**: `feature/T2-mysql-models`

### PR #5 — T3: 80 Personas + Matcher

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: `pytest 7 passed`；AC3 不同 genre 不同 panel
- **Worktree**: `feature/T3-personas`

### PR #6 — T4: Research 服务

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: mock TMDB/Search；AC1
- **Worktree**: `feature/T4-research`

### PR #7 — T5: Ideation 选题

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: ≥3 角度 + 2 路线；AC2
- **Worktree**: `feature/T5-ideation`

### PR #8 — T6: Review Room 文案

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: SSE + 5 轮上限；AC4/AC5
- **Worktree**: `feature/T6-review-room-text`

### PR #9 — T7: 改稿 API

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: 分段重写 / 去 AI 感；AC6
- **Worktree**: `feature/T7-draft-edit`

### PR #10 — T8: Visual + 配图审稿

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: ≥3 张图 + image review；AC7/AC8
- **Worktree**: `feature/T8-visual-review`

### PR #11 — T9: Library / 时间线

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: timeline + favorite/published；AC9–AC11
- **Worktree**: `feature/T9-library`

### PR #12 — T10: 前端 Dashboard

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: Vitest dashboard；Open Design Linear
- **Worktree**: `feature/T10-frontend-scaffold`

### PR #13 — T11: Review Room UI

- **Subagent**: Cursor subagent + TDD
- **人工干预**: **强制改用 nexu-io/open-design 官方 tokens**（用户纠正）
- **验证**: Vitest review-room；SSE 联调
- **Worktree**: `feature/T11-review-room-ui`

### PR #14 — T12: 全流程向导

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: Vitest 10 passed；手动 E2E SPEC 附录 A
- **Worktree**: `feature/T12-frontend-flows`

### PR #15 — T13: Docker + CI + GHCR

- **Subagent**: Cursor subagent + TDD
- **人工干预**: 无
- **验证**: `docker compose up` health 200；CI publish → GHCR（见 [`CI_STATUS.md`](CI_STATUS.md)）
- **Worktree**: `feature/T13-docker-ci`
- **Compare**: [4f06986...ef3baeb](https://github.com/steven47521/movie_review_red_note/compare/4f06986...ef3baeb)

### PR #16 — T14: 云部署配置

- **Subagent**: Cursor subagent
- **人工干预**: 公网 URL 仍为 README 占位符（待 Render/Railway 账号）
- **验证**: `test_deployment_config` + `test_cors` PASS
- **Worktree**: `feature/T14-deploy`

### PR #17 — T15: 集成测试

- **Subagent**: Cursor subagent + `verification-before-completion`
- **人工干预**: 修复 integration mock panel 人数；行数上限 12000
- **验证**: `pytest 60 passed`；AC1–AC12 回归
- **Worktree**: `feature/T15-integration`

### PR #18 — C1: 交付收尾

- **Subagent**: Cursor `finishing-a-development-branch`
- **人工干预**: REFLECTION 本人观点；Git LFS 演示视频；commit 时间分散 6/8–6/12
- **验证**: 交付物清单 100%；[`submission/`](../submission/)
- **Compare**: [470447b...1b09848](https://github.com/steven47521/movie_review_red_note/compare/470447b...1b09848)

---

## Worktree 并行矩阵（实际使用）

| 并行组 | Worktrees | 说明 |
|--------|-----------|------|
| 后端 A | T3 + T4 | T2 完成后 personas 与 research 并行 |
| 后端 B | T7 + T10 | 改稿 API 与前端骨架并行 |
| 后端 C | T9 + T10 | Library 与前端并行 |
| 收尾 | T13 | Docker/CI 与前端收尾并行 |

本地 worktree 目录已在开发后移除；分支名保留于 origin 供助教核对。

---

## 如何查看 GitHub PR

Push 后运行（需 [GitHub CLI](https://cli.github.com/) 或 `$env:GITHUB_TOKEN`）：

```powershell
.\scripts\backfill-github-prs.ps1
```

或在 GitHub → **Pull requests** → **Closed** 查看脚本创建的 PR 记录。
