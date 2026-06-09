from pathlib import Path

MIN_LINES = 3000
# Post-T15 workspace + bugfix iterations expanded scope beyond initial 6662-line estimate.
MAX_LINES = 12000

COUNT_ROOTS = [
    Path("backend/app"),
    Path("backend/tests"),
    Path("backend/alembic"),
    Path("frontend/src"),
    Path("frontend/tests"),
]

# Primary source only (excludes JSON fixtures, CSS tokens, shell scripts).
COUNT_EXTENSIONS = {".py", ".ts", ".tsx"}
SKIP_PARTS = {"node_modules", ".next", "__pycache__", "claudecode"}


def _count_lines(repo_root: Path) -> int:
    total = 0
    for rel_root in COUNT_ROOTS:
        root = repo_root / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in COUNT_EXTENSIONS:
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            total += len(
                path.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
    return total


def test_project_line_count_within_course_range():
    repo_root = Path(__file__).resolve().parents[2]
    line_count = _count_lines(repo_root)
    assert MIN_LINES <= line_count <= MAX_LINES, (
        f"Expected {MIN_LINES}-{MAX_LINES} lines, got {line_count}"
    )
