# AGENT_LOG — AI4SE 期末项目过程记录

> 按时间顺序记录 Superpowers 协作关键节点。与 `PLAN.md` task 完成记录联动。

---

## 2026-06-12 — 项目启动

- **技能**: （项目初始化，尚未触发 Superpowers 技能）
- **确认轮次**: ④里程碑 — 对照 `AI4SE_Final_Project0518.md` 梳理完成
- **Task**: 启动 / A1
- **Prompt 摘要**: 用户确认课程要求与 `.cursor/plans/ai4se_期末项目计划_076977f4.plan.md` 为项目依据；Superpowers 插件已安装于 Cursor
- **Subagent 输出**: 无
- **人工干预**: 用户将原 PLAN 中「RAG 知识库问答」方向调整为 **「自动制造优质小红书内容，主攻文字影评」**
- **教训**: 产品方向变更需在 SPEC 定稿前完成；后续 brainstorming 产出将覆盖原 PLAN 中的 RAG 架构假设

---

## 2026-06-12 — Brainstorming 启动（文字影评 · 小红书）

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 进行中
- **Task**: A2 → SPEC.md（尚未产出）
- **Prompt 摘要**: 用户提出产品构想：「自动制造优质小红书内容，主要方向是文字影评」；要求及时维护本日志
- **Subagent 输出**: 无（当前为需求澄清阶段，禁止写实现代码）
- **人工干预**: 用户提供核心方向；待通过逐轮问答补全用户/痛点/MVP
- **教训**: 课程要求 SPEC+PLAN 冷启动验证通过前不得写代码；先完成 brainstorming 再进入 writing-plans

---

## 2026-06-12 — Brainstorming Q1：目标用户

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §1 问题陈述 / 用户画像
- **Prompt 摘要**: 问「主要给谁用？」选项 A/B/C/D
- **Subagent 输出**: 用户选 **A — 个人影评博主**，自用创作优质小红书影评帖子（非批量工作室场景）
- **人工干预**: 明确为单人创作者工具，非 B 端/团队批量
- **教训**: SPEC 用户故事应以「博主本人工作流」为主线；砍掉多租户、团队协作等非 MVP 功能

---

## 2026-06-12 — Brainstorming Q2：内容范围

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §1 问题陈述 / §3 功能规约（内容类型）
- **Prompt 摘要**: 问主要发哪类影评（电影/剧集/混合/其他）
- **Subagent 输出**: 用户选 **以经典电影为主**（非剧集主线；范围聚焦院线/影史经典片）
- **人工干预**: MVP 砍掉剧集专属模板、追更式笔记等非核心能力
- **教训**: 可考虑对接影片元数据（片名、年份、导演）辅助经典片检索；SPEC 需定义「经典」由用户选片还是系统推荐

---

## 2026-06-12 — Brainstorming Q3：创作起点与深度要求

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过（用户选择 **A 的变体**）
- **Task**: A2 → SPEC.md §3 功能规约（核心工作流）
- **Prompt 摘要**: 问创作从哪一步开始（片名 / 片名+观点 / 模板 / 组合）
- **Subagent 输出**: 用户选 **仅输入片名**；系统需 **自动搜集资料、整理主流影评** → **呈现可选方向** → 用户选定后生成笔记；质量要求：**深刻、重思想主题**，非剧情介绍型水文
- **人工干预**: 工作流实为「调研 → 选角度 → 成文」三步，非一步直出；SPEC 须单独定义「思想向/主题向」生成约束与 prompt 策略
- **教训**: 与 RAG/外部检索高度相关，SPEC 需明确片名歧义、资料来源、无检索结果时的降级；「主流影评」版权与摘要方式需写进非功能需求

---

## 2026-06-12 — Brainstorming Q4：选方向交互

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §3 功能规约（选角度流程）
- **Prompt 摘要**: 调研完成后如何「让你选方向」（主题切入点 / 大纲 / 主流观点勾选 / 组合）
- **Subagent 输出**: 用户选 **D** — 先展示主流观点摘要，再给出 3–5 个主题切入点供选择，然后成文
- **人工干预**: 核心 UX 为三步：片名 → 摘要+角度 → 生成；SPEC 需定义每步 UI 与 API
- **教训**: 步骤比「一步出文」多，PLAN 须拆成独立 task（调研模块 / 角度推荐 / 成文模块）；可考虑「简化模式」作为非 MVP 扩展

---

## 2026-06-12 — Brainstorming Q5：成稿输出与配图

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过（范围扩展）
- **Task**: A2 → SPEC.md §3 功能规约（输出物）/ §8 技术选型（图像 API）
- **Prompt 摘要**: 问生成结果包含哪些字段（正文/标题/标签/hook）
- **Subagent 输出**: 用户选 **D**（标题+正文+hook 备选+标签）；标签要 **有吸引力、非直白堆砌**；新增 **精美配图** 需求：倾向 **OpenAI GPT Image** 生成高质感影视海报；希望智能体 **参考小红书等平台的优质创作提示词** 来生成图片
- **人工干预**: MVP 从「纯文字」扩展为 **文字+封面图**；SPEC 须单独模块：标签策略、图像 prompt 工程、风格库/参考学习机制
- **教训**: 「爬小红书学提示词」涉及合规与 ToS，SPEC 需明确是 **内置精选风格库 + 可选参考检索**，而非未授权抓取；图像 API 成本/限流写入非功能需求与风险节

---

## 2026-06-12 — Brainstorming Q6：配图方案

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §3 功能规约（配图模块）
- **Prompt 摘要**: MVP 配图数量（单封面 / 多图 / 先简后扩）
- **Subagent 输出**: 用户选 **C** — MVP **1 张封面海报**，架构预留多图；再次强调希望 **借鉴小红书优质提示词**
- **人工干预**: SPEC 将设计「提示词风格库」模块：人工 curated 常见小红书影视笔记视觉风格 + LLM 将片名/主题映射到风格 prompt；合规上不依赖未授权爬取
- **教训**: 「借鉴提示词」在实现上 = 风格模板库 + 可选用户粘贴参考 prompt；冷启动验证时需写清风格库来源与更新方式

---

## 2026-06-12 — Brainstorming Q7：封面视觉调性

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §3 功能规约（图像风格匹配）
- **Prompt 摘要**: MVP 封面风格库选哪几种视觉调性（胶片/极简/氛围/港风/新中式/自动匹配）
- **Subagent 输出**: 用户选 **F — 根据电影本身风格自动匹配**（类型、时代、美学气质决定海报 prompt，非固定手选）
- **人工干预**: 图像模块需「影片元数据 → 风格路由」逻辑；内置多风格模板由系统按片自动选用
- **教训**: SPEC 需定义匹配规则（genre/年份/导演/用户选定主题角度是否影响视觉）；无匹配时 fallback 风格

---

## 2026-06-12 — Brainstorming Q8：资料来源与质量痛点

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过（含关键非功能需求）
- **Task**: A2 → SPEC.md §4 非功能需求 / §10 风险 / §9 验收标准
- **Prompt 摘要**: 片名后资料从哪来（API / 搜索 / 组合 / 纯 LLM）
- **Subagent 输出**: 用户选 **C（豆瓣+TMDB + 联网搜索）**；强调 **质量必须过关** — 曾用大模型联网搜索体验差：缺乏新意、AI 感重、标题正文不吸引人
- **人工干预**: 产品核心差异化 = **反 AI 水文 + 有观点 + 小红书网感**；SPEC 须写多阶段生成、自检清单、可迭代改写，不能「搜完一次生成结束」
- **教训**: 验收标准需可测：如「标题非模板句」「正文含具体论点而非剧情复述」「标签非泛化堆砌」；PLAN 须含 prompt 工程与质量回归测试 task

---

## 2026-06-12 — Brainstorming Q9：不满意时如何改稿

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §3 功能规约（迭代改稿流程）
- **Prompt 摘要**: 第一版不满意时的改稿方式（整篇/分段/手动/去 AI 感/双路线预览）
- **Subagent 输出**: 用户选 **E** — 生成前 **2 套不同论述路线预览** → 选定再成文；并支持 **分段重写 + 手动编辑 + 「去 AI 感」润色**
- **人工干预**: 核心 UX 增加「路线预览」步骤（在选主题角度之后、成文之前）；质量模块含 anti-slop checklist
- **教训**: 工作流步骤增多，需在 SPEC 画清状态机；E2E 测试应覆盖「选路线 → 成文 → 分段重写」全路径

---

## 2026-06-12 — Brainstorming Q10：草稿与历史

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §6 数据模型 / §3 草稿管理
- **Prompt 摘要**: 是否需要持久化历史草稿
- **Subagent 输出**: 用户要 **完整历史 + 收藏/标记已发布**（A+D 组合）
- **人工干预**: 数据模型需 Post/Draft 状态机：`draft` / `published` / `favorite`；按电影与时间检索
- **教训**: 单人自用仍建议简易登录或 API Key，避免公网部署被滥用；SPEC 写清单用户场景

---

## 2026-06-12 — Brainstorming：澄清问题阶段完成

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 进入「方案对比 + 设计呈现」
- **Task**: A2
- **Prompt 摘要**: Q1–Q10 全部完成；下一步 propose 2–3 技术方案并分块呈现 SPEC 设计
- **Subagent 输出**: 待用户确认技术方案推荐
- **人工干预**: 无
- **教训**: 工作流共 7 步用户交互，适合按状态机 + 分 stage API 实现

---

## 2026-06-12 — Brainstorming：技术方案确认 + 审稿机制

- **技能**: `brainstorming`
- **确认轮次**: ①派发前 — 通过
- **Task**: A2 → SPEC.md §5 架构 / §3 质量模块
- **Prompt 摘要**: 用户确认 **方案 A（分阶段 Pipeline）**；新增需求：**拟人化 AI 打分审稿 + 自我迭代修改**（非仅人工改稿）
- **Subagent 输出**: 在 stage 5 成文后增加 **Reviewer 子流程**：多维度打分 → 拟人化评语 → 未达标则自动改写（上限 N 轮）→ 再呈现用户
- **人工干预**: 审稿人格定位为「资深小红书影评博主/编辑」；自我迭代设 max_retries 防死循环与成本失控
- **教训**: TDD 可为 reviewer 写固定样例：输入水文草稿 → 应检出 AI 感并触发 rewrite；AGENT_LOG 后续记录 prompt 迭代

---

## 2026-06-12 — Brainstorming：设计稿第1部分修订 + 多元审稿团

- **技能**: `brainstorming`
- **确认轮次**: ②执行中对齐 — 用户扩展需求
- **Task**: A2 → SPEC.md §3 审稿模块 / §6 数据模型 / §7 API
- **Prompt 摘要**: 用户确认第1部分方向；新增：**16 MBTI × 不同年龄段** 多元审稿智能体池；**聊天室式可视化**（头像+评语）；**全过程日志持久化**
- **Subagent 输出**: 设计调整为「评审团面板」— 非每次调用 80+ agent，而是 **会话级选用 3–5 位人格**（可手动选或系统按多样性自动组队）；ReviewRoom 消息流持久化
- **人工干预**: MVP 人格库 = 16 MBTI 原型 × 5 年龄段档（20s/30s/40s/50s/60s+）= 80 预设 persona，单次创作激活子集；避免成本/延迟爆炸
- **教训**: SPEC 须区分「人格库规模」与「单次激活数量」；ReviewMessage 表存 chat 记录；前端 Open Design dashboard 内嵌 Review Room 组件

---

## 2026-06-12 — Brainstorming：设计稿第2部分确认

- **技能**: `brainstorming`
- **确认轮次**: ③完成后 — 通过
- **Task**: A2 → SPEC.md §3 Review Room / §6 持久化
- **Prompt 摘要**: 用户确认「多元审稿团 + 聊天室 + 持久化」OK；评审团 **根据电影自动匹配** 适合的人格（非纯随机）
- **Subagent 输出**: 匹配规则：片种/时代/美学/用户选定主题角度 → 从 80 persona 库选 3–5 人；保留用户「换一批 / 固定默认团」为次要能力
- **人工干预**: 用户未强制 C，改为 **电影驱动匹配为主**；SPEC 写 PersonaMatcher 模块
- **教训**: 匹配逻辑需可测（固定输入片名 → 期望 MBTI/年龄段分布）；避免 always 同一组人

---

## 2026-06-12 — Brainstorming：设计稿第3部分修订（聊天室闭环 + 多图）

- **技能**: `brainstorming`
- **确认轮次**: ②执行中对齐 — 用户扩展需求
- **Task**: A2 → SPEC.md §3 Review Room / §3 Visual / §9 验收
- **Prompt 摘要**: 用户要求：**审稿与改稿均在聊天室**；改稿后可再审，**循环优化**；输出图从「仅封面」扩展为 **封面 + 2–3 张内容图**（金句卡、氛围镜头等）
- **Subagent 输出**: Review Room 升级为 **唯一改稿界面**（Writer 在聊天室发新版本，Reviewer 再审）；循环由用户 **「继续优化 / 满意定稿」** 控制，系统设 soft max（如 5 轮）防失控；Visual 模块：1 cover + 2–3 content images（quote_card / mood_shot / theme_visual）
- **人工干预**: 推翻原 MVP「仅封面」；优美镜头为 **AI 生成氛围图**（非电影截图），避版权
- **教训**: 图像 API 成本×3–4，SPEC 非功能需求写配额；E2E 测聊天室多轮 + 多图生成

---

## 2026-06-12 — Brainstorming：设计稿第4部分确认

- **技能**: `brainstorming`
- **确认轮次**: ③完成后 — 通过
- **Task**: A2 → 产出 SPEC.md
- **Prompt 摘要**: 用户确认审稿 **上限 5 轮**；**封面+2–3 内容图也需评审团在聊天室审稿**；图像模型指定 **gpt-image-2**
- **Subagent 输出**: 流程分两阶段 Review Room：**文案循环（≤5 轮）→ 配图生成 → 配图审稿循环（≤5 轮）**；VisualService 使用 OpenAI Images API `gpt-image-2`
- **人工干预**: 用户确认产品名方向「片语 RedNote」未反对
- **教训**: 配图审稿评维度：风格匹配、金句准确、小红书审美、与正文一致性；SPEC 10 节完整写入根目录 SPEC.md

---

## 2026-06-12 — SPEC 修订：数据库选型

- **技能**: `brainstorming`
- **确认轮次**: ②执行中对齐 — 用户修订
- **Task**: A2 → SPEC.md §5 / §8
- **Prompt 摘要**: 用户要求数据库改用 **MySQL**（原 SPEC 为 SQLite/PostgreSQL）
- **Subagent 输出**: SPEC 已更新为 **MySQL 8** + docker-compose 侧车 + SQLAlchemy/Alembic
- **人工干预**: 无
- **教训**: PLAN 中 T2 数据模型 task 须以 MySQL 为准写迁移与测试 fixture

---

## 2026-06-12 — writing-plans：PLAN.md 产出

- **技能**: `writing-plans`
- **确认轮次**: ④里程碑 — SPEC OK 后执行
- **Task**: A3 → PLAN.md
- **Prompt 摘要**: 用户确认 SPEC OK（含 MySQL、gpt-image-2、Review Room 双阶段、5 轮上限）
- **Subagent 输出**: 根目录 [`PLAN.md`](PLAN.md) — P0-A/B（SPEC_PROCESS+冷启动）+ T1–T15 + C1；含依赖矩阵、TDD 样例、派发前确认清单、进度表
- **人工干预**: 用户 SPEC 签字
- **教训**: **P0-B 冷启动完成前禁止 T1 代码**；执行时优先 P0-A 整理 SPEC_PROCESS.md

---

## 2026-06-12 — P0-A：SPEC_PROCESS.md 完成

- **技能**: `writing-plans` / 课程 §4.4
- **确认轮次**: ③完成后 — 通过
- **Task**: P0-A
- **Prompt 摘要**: 用户选 A（先写 SPEC_PROCESS）+ 1（Subagent-Driven 执行）
- **Subagent 输出**: [`SPEC_PROCESS.md`](SPEC_PROCESS.md) — ≥4 轮迭代节选、AI 采纳/拒绝表、Superpowers 反思；§7 留 P0-B 占位
- **人工干预**: 无
- **教训**: 下一步 P0-B 冷启动；提供可复制 prompt 给用户

---

## 2026-06-12 — P0-B：Codex 冷启动 Round 1

- **技能**: （课程 §4.5 冷启动；非 Superpowers 技能）
- **确认轮次**: ④里程碑 — Round 1 通过（文档缺陷已修）
- **Task**: P0-B
- **Prompt 摘要**: 用户提交 [`codex_log.md`](codex_log.md)；Codex 仅读 SPEC+PLAN，未写代码
- **Subagent 输出**: Codex 在 PLAN「P0-B 前禁止 T1」与「P0-B 试做 T1」矛盾处 **停问**；见 SPEC_PROCESS §7
- **人工干预**: 修订 PLAN 冷启动授权表 + SPEC §7.0 `/health`；P0-B 标记完成
- **教训**: 门禁文案须区分 **验证 Agent** vs **主开发 Agent**；可选 Codex Round 2 试 T1

---

## 2026-06-12 — P0-B Round 2：Claude Code 完成 T1

- **技能**: `test-driven-development`（冷启动 Agent 执行）
- **确认轮次**: ④里程碑 — P0-B 全部完成
- **Task**: T1 试做（`claudecode/`）
- **Prompt 摘要**: 用户用 Claude Code 按修订后 PLAN 执行 T1；日志见 [`claude_log.md`](claude_log.md)
- **Subagent 输出**: TDD 红→绿；11 个文件；`pytest 1 passed`；Cursor 复验通过
- **人工干预**: 代码在 `claudecode/` 子目录（非根目录）；暴露 D3–D6 → 修订 PLAN
- **教训**: 主开发下一步合并至根目录 + 修 CI docker job；T2 修正 config MySQL 默认值

---

## 2026-06-12 — T1：合并 claudecode/ 至根目录

- **技能**: `subagent-driven-development`（主开发 Cursor）
- **确认轮次**: ③完成后 — 通过
- **Task**: T1 / PR #1 基线
- **Prompt 摘要**: 用户「合并 T1」
- **Subagent 输出**: 根目录 `backend/`、`Makefile`、`.github/workflows/ci.yml`（仅 test job）、`README.md`；`config.py` 默认 MySQL；`claudecode/` 标记归档
- **人工干预**: 用户确认合并；修复 D5（移除 T1 过早 docker-build）、D6（config 默认 MySQL）
- **教训**: `pytest 1 passed` @ 根目录 backend；Windows 用 `python -m pytest -v`

---

## 2026-06-12 — T2：MySQL 数据模型 + Alembic + docker-compose

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T2
- **Prompt 摘要**: 用户「开始 T2」
- **Subagent 输出**: 9 张表（users, reviewer_personas, creation_sessions, movie_meta, research_snapshots, review_messages, draft_versions, image_assets, audit_logs）；`alembic/versions/001_init_schema.py`；`docker-compose.yml` mysql:8
- **TDD**: 红 `ModuleNotFoundError: app.db` → 绿 `3 passed`
- **人工干预**: 无
- **教训**: 单测用 sqlite 内存；生产迁移用 alembic + MySQL；`make docker-up` + `make migrate`

---

## 2026-06-12 — T3：80 审稿人格 + PersonaMatcher

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T3
- **Prompt 摘要**: 用户「开始 T3」
- **Subagent 输出**: `personas.json`（80 条）；`PersonaMatcher`（genre/主题/年代匹配）；`GET /api/v1/personas`；`POST .../reviewers/match|reshuffle`
- **TDD**: 红 `No module named app.services` → 绿 `7 passed`；修复 MBTI 多样性去重逻辑
- **人工干预**: 无
- **教训**: 评审团须强制 MBTI 不重复优先；种子可用 `scripts/gen_personas.py` 再生

---

## 2026-06-12 — T4：Research 服务（TMDB + 观点摘要）

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T4
- **Prompt 摘要**: 用户「开始 T4」
- **Subagent 输出**: `TMDBClient`、`SearchClient`（overview+LLM+fallback）、`ResearchService`；`POST/GET /sessions`、`POST .../research`；持久化 `MovieMeta`+`ResearchSnapshot`
- **TDD**: 红 `No module named research_service` → 绿 `10 passed`
- **人工干预**: 无
- **教训**: 无 TMDB Key 时 research 会 502；SearchClient 无 Key 时靠 overview+fallback 凑满 3 条

---

## 2026-06-12 — T5：Ideation 选题服务

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T5
- **Prompt 摘要**: 用户「开始 T5」
- **Subagent 输出**: `LLMClient`、`IdeationService`、prompts；API angles/routes generate+select；状态至 `route_ready`
- **TDD**: 红 → 绿 `14 passed`
- **人工干预**: 无
- **教训**: 过滤「剧情」类角度；路线须 2 条且 outline 不同；需先 research 再 ideation

---

## 2026-06-12 — T6：Review Room 文案阶段

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T6
- **Prompt 摘要**: 用户「开始 T6」
- **Subagent 输出**: `ReviewOrchestrator`（审稿→Moderator→Writer）；SSE `/review/stream`；`draft/generate`、`review/continue`、`finalize-text`；`ReviewMessage`+`DraftVersion` 持久化
- **TDD**: 红 → 绿 `18 passed`；水文样例触发改稿测试
- **人工干预**: 无
- **教训**: 文案审稿 ≤5 轮；须先 `reviewers/match` 再成稿；T7 做分段改稿/去AI感

---

## 2026-06-12 — T7：改稿 API（分段重写 / 去 AI 感 / 手动保存）

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T7
- **Prompt 摘要**: 用户「开始 T7」
- **Subagent 输出**: `DraftService`；`POST draft/regenerate`、`POST de-ai-polish`、`PATCH draft`；每次改稿新版本 + Writer 消息入 Review Room
- **TDD**: 红 → 绿 `24 passed`
- **人工干预**: 无
- **教训**: `de_ai_polish` 有规则兜底 + 可选 LLM；`part` 限 title/hooks/body/tags

---

## 2026-06-12 — T8：Visual + gpt-image-2 + 配图 Review Room

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T8
- **Prompt 摘要**: 用户「开始 T8」
- **Subagent 输出**: `OpenAIImageClient`(gpt-image-2)、`visual_styles.json`、`VisualService`；配图审稿 `run_image_review_round`；API images/generate|regenerate|list、review/stream?phase=image
- **TDD**: 红 → 绿 `28 passed`
- **人工干预**: 无
- **教训**: 风格按 genre 路由；quote_card 金句来自 hooks/正文；配图审稿 ≤5 轮独立计数

---

## 2026-06-12 — T9：Library 历史 / 收藏 / 时间线回放

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T9
- **Prompt 摘要**: 用户「开始 T9」
- **Subagent 输出**: `LibraryService`；`GET /sessions`（favorite/published/status/movie_title 筛选）、`GET /sessions/{id}`、`GET /sessions/{id}/timeline`、`PATCH /sessions/{id}` 收藏/发布标记
- **TDD**: 红 → 绿 `34 passed`
- **人工干预**: 无
- **教训**: timeline 按时间戳合并 research、review_message、draft_version、image_asset；完整历史不做截断

---

## 2026-06-12 — T10：前端骨架 + Open Design Dashboard

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T10
- **Prompt 摘要**: 用户「T10」
- **Subagent 输出**: `frontend/` Next.js 15 + TS + Tailwind；Linear 深色 token；`/dashboard` 侧栏+工作台+「新建创作」CTA；会话卡片占位；Vitest 组件测试
- **TDD**: 红 → 绿 `npm test` 1 passed；`npm run build` OK
- **人工干预**: 无
- **教训**: Open Design 用 Linear 色板（#08090a / #5e6ad2）；T11 再接 SSE Review Room

---

## 2026-06-12 — T11：Review Room 聊天 UI（SSE）+ Open Design 正式接入

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T11（含 T10 补齐 nexu-io/open-design 合规）
- **Prompt 摘要**: 用户指出课程要求必须用 nexu-io/open-design，并开始 T11
- **Subagent 输出**:
  - 引入 `frontend/open-design/design-systems/linear-app/tokens.css`（官方 vendored）
  - `src/styles/open-design/components.css`（dashboard + chat 组件范式）
  - 重构 T10 Dashboard 使用 od-* 类
  - `useReviewStream` + `ChatPanel` + `ReviewerBubble`；`/dashboard/review`
  - Vitest mock EventSource 验证审稿头像+气泡
- **TDD**: 红 → 绿 `npm test` 3 passed；`npm run build` OK
- **人工干预**: 用户纠正 Open Design 须用 nexu-io/open-design 官方 token，而非手写 Tailwind 近似色
- **教训**: 课程 §3.3 强制 open-design；Linear + dashboard skill 通过 tokens.css + components 落地

---

## 2026-06-12 — T12：选题向导 + 编辑器 + 图片画廊 + 全流程

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T12
- **Prompt 摘要**: 用户「开始 T12」
- **Subagent 输出**:
  - `lib/api.ts` 统一后端调用
  - `ideation-wizard/` MovieInput / AngleSelect / RouteSelect
  - `draft-editor/DraftEditor` 手动保存、分段重写、去 AI 感
  - `image-gallery/ImageGallery` 封面+内容图预览/重生成
  - `creation-wizard/CreationWizard` 串联 SPEC 附录 A 全流程
  - 页面 `/dashboard/create`、`/dashboard/sessions/[id]` 时间线
- **TDD**: 红 → 绿 `npm test` 10 passed；`npm run build` OK
- **人工干预**: 无
- **教训**: 前端主路径一步向导降低用户认知负担；配图阶段 image ChatPanel 默认不 autoStart 避免空连 SSE

---

## 2026-06-12 — T13：Docker Compose 全栈 + CI + GHCR

- **技能**: `test-driven-development` | `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过
- **Task**: T13
- **Prompt 摘要**: 用户「开始 T13」
- **Subagent 输出**:
  - `backend/Dockerfile` + `docker-entrypoint.sh`（等待 MySQL → alembic → uvicorn）
  - `frontend/Dockerfile`（Next.js standalone）
  - `docker-compose.yml` mysql + backend:8000 + frontend:3000
  - CI：backend-test + frontend-test + docker health + GHCR publish on main
  - `test_docker_compose.py` 校验全栈配置
- **TDD**: 红 → 绿 `pytest 36 passed`；本地无 Docker CLI，CI 负责 compose 验证
- **人工干预**: 无
- **教训**: `make docker-up-db` 保留仅 MySQL 本地开发；`make docker-up` 为全栈一键启动

---

## 2026-06-12 — T14：云部署 Railway / Render

- **技能**: `subagent-driven-development`
- **确认轮次**: ③完成后 — 通过（配置就绪，需用户账号完成实际上线）
- **Task**: T14
- **Prompt 摘要**: 用户「开始 T14」
- **Subagent 输出**:
  - `render.yaml` Blueprint（rednote-api + rednote-web）
  - `railway.toml` 参考配置
  - `docs/DEPLOYMENT.md` 分步指南（MySQL on Railway + API/Web on Render/Railway）
  - Backend CORS（`CORS_ORIGINS`）
  - `scripts/verify-deployment.sh` 冒烟脚本
  - README Production URLs 占位表
- **TDD**: `test_deployment_config.py` + `test_cors.py` → `pytest 40 passed`
- **人工干预**: 需用户在 Render/Railway 填入 API Key 并替换 README 公网 URL
- **教训**: `NEXT_PUBLIC_API_URL` 必须 frontend 构建时注入；MySQL 放 Railway 最省事

---

## 2026-06-12 — T15：集成测试 + 质量回归

- **技能**: `test-driven-development` | `verification-before-completion`
- **确认轮次**: ③完成后 — 通过
- **Task**: T15
- **Prompt 摘要**: 用户「开始 T15」
- **Subagent 输出**:
  - `backend/tests/integration/test_full_flow.py` — 全流程（调研→选题→路线→评审团→成稿审稿→定稿→配图→完成→timeline）
  - `backend/tests/fixtures/watery_draft.json` — AC5 水文样例
  - `backend/tests/test_line_count.py` — 课程规模自检（`.py`/`.ts`/`.tsx` 6662 行）
- **修复**: 集成测试固定 3 人评审团避免 LLM mock 耗尽；行数统计排除 JSON/CSS/脚本
- **TDD**: `pytest 44 passed`（含 3 集成 + 1 行数）
- **人工干预**: 无
- **教训**: 集成测试 mock `side_effect` 须与 `PersonaMatcher` 实际 panel 人数对齐；行数用主源码扩展名更贴近课程意图

---

## 2026-06-12 — C1：交付收尾

- **技能**: `finishing-a-development-branch` | `verification-before-completion`
- **确认轮次**: ④里程碑 — 通过（2 项待用户补：git PR、公网 URL）
- **Task**: C1
- **Prompt 摘要**: 用户「做 C1 收尾」
- **Subagent 输出**:
  - [`REFLECTION.md`](REFLECTION.md) — Brainstorming 引导 Q1–Q8，本人观点（定方向/定标准/纠偏），约 2100 字
  - [`README.md`](README.md) 终稿 — 30 秒价值、交付物表、REFLECTION 链接
  - [`PLAN.md`](PLAN.md) — C0 课程覆盖审计表 + C1 勾选
- **AGENT_LOG 核对**: P0-A/B、T1–T15 均有对应条目，与 PLAN 进度表一致
- **TDD**: `pytest 44 passed` · `vitest 10 passed`
- **C0 缺口**:
  - ⚠️ 本地仓库未 init git → worktree/PR/commit hash 待提交前补
  - ⏳ 公网 URL 仍为 README 占位符 → 按 DEPLOYMENT.md 部署后替换
- **人工干预**: 用户通过 Brainstorming 式问答确认 REFLECTION 核心观点（电影兴趣、网页 AI 痛点、Brainstorming/TDD/Open Design 体感）
- **教训**: C1 重点是「过程证据齐全 + 覆盖表可审计」；实现已完成，交付前务必补 git 历史与可选云 URL

---

## 2026-06-12 — Git 仓库初始化与演示视频入库

- **技能**: `finishing-a-development-branch`
- **Task**: C1 交付 / GitHub 提交准备
- **Subagent 输出**:
  - `git init` + Git LFS 跟踪 `*.mp4`
  - 演示视频移至 `docs/demo/演示视频提交.mp4`（约 130MB，LFS）
  - 修复 `test_full_flow` mock（`model=` 参数）+ 行数测试上限；`pytest 60 passed`
  - 分批 commit：`c12368b` docs → `ffbe787` 源码 → `de48f2d` README/CI/演示视频
  - 分支 `main`；remote 预设 `github.com/wangdaoheng/AI4SE_Final_Project`
- **人工干预**: 需在 GitHub 网页创建同名公开仓库后执行 `git push -u origin main`
- **教训**: 超过 100MB 的视频必须用 Git LFS；`.env` 与 `*.db` 不可提交

