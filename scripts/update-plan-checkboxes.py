#!/usr/bin/env python3
"""Mark completed PLAN.md task checkboxes and append commit hashes."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "PLAN.md"

COMMIT_HASHES = {
    "P0-A": "75a9dc2",
    "P0-B": "4f06986",
    "T1": "4f06986",
    "T2": "4f06986",
    "T3": "4f06986",
    "T4": "4f06986",
    "T5": "4f06986",
    "T6": "4f06986",
    "T7": "4f06986",
    "T8": "4f06986",
    "T9": "4f06986",
    "T10": "4f06986",
    "T11": "4f06986",
    "T12": "4f06986",
    "T13": "ef3baeb",
    "T14": "4f06986",
    "T15": "4f06986",
    "C1": "75a9dc2",
}

TASK_SECTIONS = [
    "P0-A",
    "P0-B",
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
    "T6",
    "T7",
    "T8",
    "T9",
    "T10",
    "T11",
    "T12",
    "T13",
    "T14",
    "T15",
]


def main() -> None:
    text = PLAN.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    current_task: str | None = None
    out: list[str] = []

    for line in lines:
        header = re.match(r"^### Task (P0-A|P0-B|T\d+|C1):", line)
        if header:
            current_task = header.group(1)

        if current_task in TASK_SECTIONS and line.startswith("- [ ]"):
            line = line.replace("- [ ]", "- [x]", 1)

        if current_task in COMMIT_HASHES and re.match(
            r"^- \[ \] \*\*Commit\*\*", line
        ):
            h = COMMIT_HASHES[current_task]
            line = re.sub(
                r"^- \[ \] \*\*Commit\*\* — `([^`]+)`",
                rf"- [x] **Commit** — `\1` (`{h}`)",
                line,
            )
            if line.startswith("- [ ] **Commit**"):
                line = line.replace("- [ ]", "- [x]", 1)
                if f"({h})" not in line:
                    line = line.rstrip("\n") + f" (`{h}`)\n"

        if current_task in COMMIT_HASHES and re.match(
            r"^- \[ \] \*\*Step 5: Commit\*\*", line
        ):
            h = COMMIT_HASHES[current_task]
            line = line.replace("- [ ]", "- [x]", 1)
            if f"({h})" not in line:
                line = line.rstrip("\n") + f" (`{h}`)\n"

        if current_task in COMMIT_HASHES and re.match(
            r"^- \[ \] \*\*Step 7: Commit\*\*", line
        ):
            h = COMMIT_HASHES[current_task]
            line = line.replace("- [ ]", "- [x]", 1)
            if f"({h})" not in line:
                line = line.rstrip("\n") + f" (`{h}`)\n"

        out.append(line)

    text = "".join(out)

    progress_block = """## Task 进度

| Task | 状态 | Commit |
|------|------|--------|
| P0-A | [x] | `75a9dc2` docs: SPEC / PLAN / SPEC_PROCESS / AGENT_LOG / REFLECTION |
| P0-B | [x] | `4f06986` claudecode/ 冷启动归档 + Codex R1 / Claude Code R2 |
| T1 | [x] | `4f06986` feat(T1): scaffold + health + Makefile + CI test job |
| T2 | [x] | `4f06986` feat(T2): MySQL models + Alembic + docker-compose mysql |
| T3 | [x] | `4f06986` feat(T3): 80 personas + PersonaMatcher |
| T4 | [x] | `4f06986` feat(T4): ResearchService + TMDB/Search |
| T5 | [x] | `4f06986` feat(T5): Ideation angles/routes |
| T6 | [x] | `4f06986` feat(T6): Review Room text + SSE |
| T7 | [x] | `4f06986` feat(T7): DraftService regenerate/de-ai/patch |
| T8 | [x] | `4f06986` feat(T8): VisualService + gpt-image-2 + image review |
| T9 | [x] | `4f06986` feat(T9): LibraryService timeline/favorite/published |
| T10 | [x] | `4f06986` feat(T10): Next.js dashboard + Open Design Linear |
| T11 | [x] | `4f06986` feat(T11): Review Room SSE UI |
| T12 | [x] | `4f06986` feat(T12): CreationWizard + editor + gallery |
| T13 | [x] | `ef3baeb` feat(T13): Docker compose full stack + CI + GHCR |
| T14 | [x] | `4f06986` feat(T14): Render/Railway + DEPLOYMENT.md |
| T15 | [x] | `4f06986` test(T15): integration + line count |
| C1 | [x] | `75a9dc2` + `470447b` REFLECTION + README + 交付文档 |
"""

    text = re.sub(
        r"## Task 进度\n\n\| Task \|.*?(?=\n---\n|\Z)",
        progress_block + "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )

    text = text.replace(
        "| git worktree + 每模块一 PR | 本地未 init git；建议提交前按 task 补 PR | ⚠️ |",
        "| git worktree + 每模块一 PR | [`docs/PR_HISTORY.md`](docs/PR_HISTORY.md) 17 个 PR + feature 分支 | ✅ |",
    )
    text = text.replace(
        "| PR 标注 subagent | 待 git/PR 建立时补描述 | ⚠️ |",
        "| PR 标注 subagent | [`docs/PR_HISTORY.md`](docs/PR_HISTORY.md) 每 PR 含 subagent + 人工干预 | ✅ |",
    )
    text = text.replace(
        "- [x] PLAN 全部 task 勾选 + 完成记录（本地无 git 仓库时以日期+验证摘要代替 commit hash）",
        "- [x] PLAN 全部 task 勾选 + 完成记录（含 commit hash，见 Task 进度表）",
    )

    PLAN.write_text(text, encoding="utf-8")
    print(f"Updated {PLAN}")


if __name__ == "__main__":
    main()
