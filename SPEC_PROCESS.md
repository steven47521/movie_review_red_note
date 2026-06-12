# SPEC_PROCESS.md — 规约与计划协作过程记录

> 项目：**片语 RedNote**（经典电影小红书创作助手）  
> 主开发 Agent：**Cursor Agent + Superpowers**  
> 文档范围：brainstorming → SPEC.md → PLAN.md → **P0-B 冷启动**（§7 Round 1+2 已完成）

---

## 1. 过程概览

| 阶段 | 时间 | 技能 | 产出 |
|------|------|------|------|
| 项目启动 | 2026-06-12 | — | 确认课程要求；方向从 RAG 知识库改为小红书影评 |
| Brainstorming Q1–Q10 | 2026-06-12 | `brainstorming` | 用户画像、工作流、质量痛点 |
| 设计稿分块确认 | 2026-06-12 | `brainstorming` | 4 部分设计 + 方案 A Pipeline |
| SPEC 定稿 | 2026-06-12 | `brainstorming` | [`SPEC.md`](SPEC.md) |
| SPEC 修订 | 2026-06-12 | `brainstorming` | MySQL、gpt-image-2、配图审稿 |
| PLAN 定稿 | 2026-06-12 | `writing-plans` | [`PLAN.md`](PLAN.md) |
| 冷启动验证 | 2026-06-12 | Codex R1 + Claude Code R2 | **P0-B 完成**（§7） |

---

## 2. Brainstorming 关键节点

### 2.1 智能体提出的关键问题（及作用）

| 序号 | 智能体问题 | 作用 |
|------|------------|------|
| Q1 | 主要给谁用？（个人博主 / 普通观众 / 工作室） | 锁定 **单人创作者**，砍掉 B 端与多租户 |
| Q2 | 发电影还是剧集？ | 聚焦 **经典电影**，砍掉追更与分集逻辑 |
| Q3 | 从片名还是片名+观点开始？ | 暴露用户真实流程：**只输入片名**，但要 **思想深度** |
| Q4 | 选方向 UI：切入点 / 大纲 / 主流观点 / 组合？ | 定为 **主流摘要 + 主题切入点（D）** |
| Q5 | 输出含哪些字段？ | 扩展为 **标题+hook+正文+网感标签** |
| Q6–Q7 | 配图数量与视觉调性？ | 从单封面演化为 **自动按片匹配风格** |
| Q8 | 资料从哪来？ | 确认 **TMDB+豆瓣+搜索**；记录 **质量失败经历** |
| Q9 | 不满意怎么改？ | 引入 **双路线预览（E）** |
| Q10 | 要不要历史草稿？ | **完整历史 + 收藏/已发布** |

### 2.2 用户修正了哪些原设想

| 原设想（Agent 或初始 PLAN） | 用户修正 | 原因 |
|-----------------------------|----------|------|
| RAG 知识库问答 | 小红书 **文字影评** 创作 | 用户真实需求是 **内容生产**，不是文档问答 |
| 纯文字 MVP | 封面 + 内容图 + **配图也要审稿** | 小红书笔记是 **图文一体** |
| 仅 1 张封面（方案 C） | 封面 + **2–3 张内容图** | 金句卡、氛围图是常见优质笔记形态 |
| 随机或固定评审团 | **按电影气质自动匹配** 3–5 人 | 不同片种需要不同读者视角 |
| PostgreSQL/SQLite | **MySQL 8** | 用户技术偏好 |
| 审稿改稿分页面 | **全部在 Review Room 聊天室** | 过程可见、可回放、更符合「讨论式创作」 |

---

## 3. 关键迭代（≥3 轮，含对话节选与决策）

### 迭代 1：产品方向 Pivot（RAG → 小红书影评）

**对话节选：**

- **用户：** 「我想开发一个自动制造优质小红书内容的产品，主要的方向是文字影评。」  
- **Agent：** 「30 秒版理解：上传资料→RAG 问答（原 PLAN） vs 你的方向：输入片名→调研→思想向笔记？」  
- **决策：** 废弃原 `.cursor/plans` 中 RAG 架构假设；brainstorming 从零定义 **片语 RedNote**。

**处理决策：** 接受 pivot；SPEC/PLAN 全部按新方向重写，不在旧模块上打补丁。

---

### 迭代 2：质量痛点 → 双路线 + 多元审稿团

**对话节选：**

- **用户：** 「我用大模型联网搜索做过，结果没什么新意，AI 感也很重，标题和内容也不吸引人。」  
- **Agent：** 推荐方案 **E**：成文前先给 **2 套论述路线**；后扩展 **拟人化 AI 审稿 + 自我迭代**。  
- **用户：** 「审稿人格可以更加多元…16 种 MBTI × 不同年龄段…聊天室一样，每个 agent 有头像。」

**处理决策：**

- **采纳：** 分阶段 Pipeline（方案 A）、双路线预览、Review Room、80 persona 库（单次激活 3–5 人）。  
- **Agent 约束用户：** 80 人不可每篇全员审稿 → 用户接受 **电影驱动匹配子集**。  
- **写入 SPEC：** 文案审稿 ≤5 轮；Moderator + Writer 闭环。

---

### 迭代 3：配图范围 + 配图审稿 + 技术定稿

**对话节选：**

- **Agent：** 「MVP 先做 1 张封面？」  
- **用户：** 「C 吧…还需要 2–3 张内容图，金句、优美镜头；用 gpt image 2。」  
- **用户：** 「封面+内容图也需要评审团审。」  
- **用户：** 「审稿轮次上限 5 轮。」  
- **用户：** 「数据库用 MySQL。」 → **用户：** 「SPEC OK。」

**处理决策：**

- **采纳：** Visual 模块 1 cover + 2–3 content images；**独立配图审稿阶段** ≤5 轮；`gpt-image-2`；MySQL 8。  
- **Agent 约束：** 「优美镜头」= **AI 氛围图**，禁止剧照截图（版权）；「学小红书 prompt」= **curated 风格库**，不爬站。用户未反对。

---

### 迭代 4（writing-plans）：执行策略

**对话节选：**

- **Agent：** 「P0-A 写 SPEC_PROCESS / P0-B 冷启动 / 再 T1…选 Subagent 或 Inline？」  
- **用户：** 「A，1」→ 先写 SPEC_PROCESS；实现阶段用 **Subagent-Driven**。

**处理决策：** PLAN 保留 P0-B 门禁；T1–T15 每 task 独立 worktree + subagent。

---

## 4. AI 建议 vs 人工裁决

| AI 建议 | 结果 | 原因 |
|---------|------|------|
| 原 PLAN：RAG 知识库 | **推翻** | 与用户真实目标不符 |
| 资料方案 C（API+搜索） | **采纳** | 平衡中文观点与元数据准确性 |
| 方案 A 分阶段 Pipeline | **采纳** | 质量需分步控，不能一次生成 |
| MVP 仅 1 张封面 | **部分推翻** | 用户要 2–3 内容图 + 配图审稿 |
| 爬小红书学 prompt | **拒绝** | 合规与 ToS；改为 curated 风格库 |
| 80 人全员审稿 | **拒绝** | 成本与可读性；改为 3–5 人 + 电影匹配 |
| PostgreSQL | **推翻** | 用户指定 MySQL |
| 评审团默认「固定团+换一批」(C) | **修正** | 用户要 **按电影自动匹配** 为主 |
| 无限审稿循环 | **限制为 5 轮** | 用户确认上限；Agent 补充成本风控 |
| Open Design Linear + dashboard | **采纳** | 契合创作台 + 聊天室 UI |

---

## 5. Superpowers Brainstorming 技能反思

### 5.1 做得好的地方

1. **一次一问**：避免信息过载；用户（非技术背景）能逐步回答 A/B/C/D。  
2. **主动 scope 控制**：在 80 persona、爬小红书、全员审稿等点上 **主动拦**，避免期末项目爆炸。  
3. **分块设计签字**：问题陈述 → 审稿团 → 数据/API → 技术选型，用户每块 OK 再写 SPEC，减少返工。  
4. **与课程对齐**：自动映射 SPEC 10 节、Open Design、TDD、冷启动门禁到 PLAN。

### 5.2 不满或局限

1. **初始 PLAN 假设未被第一时间清空**：用户第一句就 pivot，若未 reread 会残留 RAG 架构。  
2. **配图需求出现较晚**：Q5–Q6 才展开，导致 SPEC 经历一次「纯文字→图文」大改；更早问「小红书笔记长什么样」更好。  
3. **一次一问拖长会话**：10+ 轮才定稿，过程文档需靠 AGENT_LOG 补，否则易丢上下文。  
4. **无法替用户验证 gpt-image-2 可用性**：模型名写入 SPEC，实际 API 以部署时为准，冷启动应暴露此歧义。

### 5.3 可复用 prompt 策略

- 开场强制三问：**谁用 / 什么痛点 / 30 秒电梯演讲**。  
- 任何「AI 生成内容」产品追加：**质量失败案例 / 反 AI 感验收 / 迭代 UI**。  
- 涉及 UGC 平台时提前问：**输出是纯文还是图文 / 要不要持久化历史**。

---

## 6. Writing-plans 阶段记录

- **输入：** 用户「SPEC OK」+ MySQL 修订。  
- **产出：** [`PLAN.md`](PLAN.md) — 17 个 task（P0-A/B, T1–T15, C1），含依赖矩阵、TDD 样例、派发前确认清单。  
- **执行选择：** Subagent-Driven（用户选 1）。  
- **门禁：** P0-B 冷启动完成前 **禁止 T1 代码**。

---

## 7. 冷启动验证（P0-B）

> 原始日志：[`codex_log.md`](codex_log.md)

### 7.1 执行概况

| 项 | 内容 |
|----|------|
| 日期 | 2026-06-12 |
| 验证 Agent | **OpenAI Codex CLI**（与 Cursor 主开发不同类型） |
| 输入约束 | 仅 `SPEC.md` + `PLAN.md`，新 session |
| 计划任务 | T1（+ 可选 T2） |
| 实际结果 | **未写代码**；读完文档后在 PLAN 门禁处 **主动停问** |

### 7.2 验证 Agent 停问点

Codex 引用 PLAN 原文：

```text
⛔ 在 P0-B 完成且 SPEC/PLAN 修订合并前，禁止开始 T1 实现代码。
```

并提问：应 (1) 等待 (2) 先完成 P0-B (3) 无视门禁做 T1？

**结论：** Agent **未猜测、未 bypass**，行为符合课程「不确定就停问」——但也暴露 **PLAN 自相矛盾**。

### 7.3 暴露的 SPEC/PLAN 缺陷

| # | 缺陷 | 严重性 | 说明 |
|---|------|--------|------|
| D1 | **P0-B 与 T1 门禁矛盾** | Critical | P0-B 要求「试做 T1」，同文档又写「P0-B 完成前禁止 T1」；陌生 agent 无法判断 |
| D2 | **`/health` 仅在 PLAN 出现** | Minor | SPEC 未写 bootstrap 健康检查，Codex 正确注意到「SPEC 无、PLAN 有」 |

**非误解（Agent 读对的部分）：**

- T1 文件清单、TDD 步骤、Python 3.12 + FastAPI、`make test` 均来自 PLAN，与 SPEC 一致。  
- P0-A 已完成、P0-B 未勾选——Agent 正确读取进度表。

### 7.4 修订（修订前后 diff）

**PLAN.md — 门禁表述**

```diff
- > ⛔ 在 P0-B 完成且 SPEC/PLAN 修订合并前，禁止开始 T1 实现代码。
+ **冷启动授权（与 Phase B 门禁的关系）：**
+ | P0-B 验证 Agent | ✅ 可以试做 T1/T2 | 产物可丢弃 |
+ | 主开发 Agent     | ⛔ 禁止 T1 正式 PR | 须 P0-B 记录+修订合并后 |
+ > Phase B 主开发门禁：… P0-B 验证 Agent 试做 T1 不受此限。
```

**SPEC.md — 补充 Bootstrap API**

```diff
+ ### 7.0 脚手架与健康检查（T1 Bootstrap）
+ | GET | /health | 200 {"status":"ok"} |
```

### 7.5 产出与预期差距

| 预期 | 实际 | 评估 |
|------|------|------|
| 试做 T1 并暴露实现歧义 | 在门禁处停止，零代码 | **仍有价值**：发现 Critical 文档缺陷 |
| 1–2 小时实现片段 | ~15 分钟读文档 + 1 个问题 | 建议 **可选 Round 2**：用修订后 PLAN 再跑 T1 |

### 7.6 是否允许主开发开始 T1？

| 条件 | 状态 |
|------|------|
| 冷启动记录写入 SPEC_PROCESS | ✅ 本节 |
| SPEC/PLAN 修订合并 | ✅ D1/D2 已修 |
| 可选 Round 2 | 建议用户用 Codex 再试 T1；**非阻塞**主开发 |

**裁决：** P0-B Round 1 **完成**；主开发可按 Subagent-Driven 开始 **T1**。

---

### 7.7 Round 2：Claude Code 试做 T1

> 原始日志：[`claude_log.md`](claude_log.md)  
> 代码目录：[`claudecode/`](claudecode/)（冷启动试做，**非主仓库根目录**）

| 项 | 内容 |
|----|------|
| 日期 | 2026-06-12 |
| 验证 Agent | **Claude Code**（claude-sonnet-4.6，与 Cursor/Codex 均不同） |
| 输入 | `SPEC.md` + `PLAN.md`（修订后）+ 用户指定输出到 `claudecode/` |
| 任务 | **T1 only** |
| TDD | ✅ 红（ModuleNotFoundError）→ 绿（1 passed） |
| 本地复验 | Cursor 复跑 `pytest` → **1 passed** |

**实现与 SPEC 对齐情况：**

| 验收项 | 结果 |
|--------|------|
| `GET /health` → `200 {"status":"ok"}` | ✅ |
| `Makefile` + `make test` | ✅ 已写；Windows 无 `make`，用 `python -m pytest -v` 代替 |
| CI pytest job | ✅ Python 3.12 |
| 未做 T2+ | ✅ 符合范围 |

**Round 2 暴露的问题（非误解）：**

| # | 问题 | 严重性 | 处理 |
|---|------|--------|------|
| D3 | Windows 无 `make` | 中 | PLAN T1 补充 Windows 等价命令 |
| D4 | 本地 Python 3.10 ≠ PLAN 3.12 | 低 | CI 用 3.12；本地 3.10+ 可开发 |
| D5 | CI `docker-build` 无 `Dockerfile` | 中 | T1 仅保留 test job；docker 延后 T13 |
| D6 | `config.py` 默认 `sqlite://` | 低 | T2 改为 MySQL 占位；T1 仅环境变量骨架 |

**Agent 未停问、自行处理的项：**

- 代码放 `claudecode/`（用户指令，合理）
- `requirements.txt` pin 版本（PLAN 未写，自行补充，可复现）

**修订 diff（Round 2 后）：**

```diff
# PLAN.md T1 验证
+ Windows 开发：`cd backend && python -m pytest -v` 等价于 `make test`
+ T1 CI workflow 仅 pytest job；docker-build 移至 T13

# .env.example / config.py（T2 时）
- DATABASE_URL 默认 sqlite
+ DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/rednote
```

### 7.8 P0-B 总结

| Round | Agent | 结果 |
|-------|-------|------|
| 1 | Codex | 发现 PLAN 门禁矛盾；零代码 |
| 2 | Claude Code | **T1 完整 TDD 通过**；代码在 `claudecode/` |

**P0-B 状态：✅ 完成**（满足课程「不同 agent + 试做 1–2 task + 修订 SPEC/PLAN」）

**主开发 T1：** 须将 `claudecode/` 产物**合并到仓库根目录**（或以此为基线开 `feature/T1-scaffold` PR），并修复 D5/D6。

---

## 8. 当前文档状态

| 文档 | 状态 |
|------|------|
| [`SPEC.md`](SPEC.md) | ✅ 用户签字 + 冷启动修订（§7.0 health） |
| [`PLAN.md`](PLAN.md) | ✅ Round 2 后待合并 D3–D5 修订 |
| [`SPEC_PROCESS.md`](SPEC_PROCESS.md) | ✅ §7 Round 1+2 完整 |
| [`AGENT_LOG.md`](AGENT_LOG.md) | 🔄 持续更新 |
| [`codex_log.md`](codex_log.md) | ✅ Round 1 |
| [`claude_log.md`](claude_log.md) | ✅ Round 2 |
| [`claudecode/`](claudecode/) | ✅ T1 冷启动试做代码 |
| 主仓库根目录 `backend/` | ✅ T1 已合并（2026-06-12） |
| [`claudecode/`](claudecode/) | 归档（冷启动试做，以根目录为准） |

---

## 9. 下一步

1. ~~P0-B Round 1（Codex）~~ ✅  
2. ~~P0-B Round 2（Claude Code T1）~~ ✅  
3. ~~合并 `claudecode/` → 根目录~~ ✅  
4. **Subagent-Driven** 继续 **T2**（MySQL 模型 + Alembic）
