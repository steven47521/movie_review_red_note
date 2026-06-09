import re

from sqlalchemy.orm import Session

from app.llm.client import LLMClient, LLMClientError
from app.models.creation_session import CreationSession
from app.models.draft_version import DraftVersion
from app.models.review_message import MessageRole, ReviewPhase, ReviewMessage

VALID_PARTS = {"title", "hooks", "body", "tags"}

BANNED_PHRASES = [
    "综上所述",
    "总而言之",
    "不难发现",
    "深刻地揭示了人性的复杂",
    "这部电影深刻地",
    "值得一看",
    "非常好看",
]

DE_AI_SYSTEM = """你是小红书文案去 AI 感润色编辑。
删除套话、空泛句，保留核心观点，输出更口语、更有网感的中文。
返回 JSON：{"body": "润色后正文"}
"""

REGENERATE_SYSTEM = """你是小红书影评文案编辑。
只重写指定部分，其它部分保持不变。
返回 JSON，仅包含需要重写的字段。
"""


class DraftServiceError(Exception):
    pass


class DraftService:
    def __init__(self, db: Session | None = None, llm_client: LLMClient | None = None):
        self.db = db
        self.llm = llm_client or LLMClient()

    def regenerate_part(self, session_id: str, part: str) -> DraftVersion:
        if part not in VALID_PARTS:
            raise DraftServiceError(f"Invalid part: {part}. Must be one of {VALID_PARTS}")
        if not self.db:
            raise DraftServiceError("Database session required")

        current = self._latest_draft(session_id)
        if not current:
            raise DraftServiceError(f"No draft for session: {session_id}")

        prompt = (
            f"电影文案当前内容：\n"
            f"标题：{current.title}\n"
            f"Hooks：{current.hooks}\n"
            f"正文：{current.body}\n"
            f"标签：{current.tags}\n"
            f"请只重写 part={part}，使其更有小红书吸引力，避免 AI 套话。"
        )
        try:
            data = self.llm.complete_json(REGENERATE_SYSTEM, prompt)
        except LLMClientError as exc:
            raise DraftServiceError(str(exc)) from exc

        new_data = {
            "title": current.title,
            "hooks": list(current.hooks),
            "body": current.body,
            "tags": list(current.tags),
        }
        if part == "title":
            new_data["title"] = data.get("title") or current.title
        elif part == "hooks":
            new_data["hooks"] = data.get("hooks") or current.hooks
        elif part == "body":
            new_data["body"] = data.get("body") or current.body
        elif part == "tags":
            new_data["tags"] = data.get("tags") or current.tags

        return self._save_version(
            session_id,
            new_data,
            review_round=current.review_round,
            writer_note=f"Writer 已分段重写：{part}",
        )

    @staticmethod
    def de_ai_polish(text: str) -> str:
        polished = text
        for phrase in BANNED_PHRASES:
            polished = polished.replace(phrase, "")
        polished = re.sub(r"\s{2,}", " ", polished).strip()
        polished = re.sub(r"^[，,。\s]+", "", polished)
        return polished or text

    def apply_de_ai_polish(self, session_id: str) -> DraftVersion:
        if not self.db:
            raise DraftServiceError("Database session required")

        current = self._latest_draft(session_id)
        if not current:
            raise DraftServiceError(f"No draft for session: {session_id}")

        try:
            if self.llm.api_key:
                data = self.llm.complete_json(
                    DE_AI_SYSTEM,
                    f"请润色以下正文，去除 AI 套话：\n{current.body}",
                )
                body = data.get("body") or self.de_ai_polish(current.body)
            else:
                body = self.de_ai_polish(current.body)
        except LLMClientError:
            body = self.de_ai_polish(current.body)

        new_data = {
            "title": current.title,
            "hooks": list(current.hooks),
            "body": body,
            "tags": list(current.tags),
        }
        return self._save_version(
            session_id,
            new_data,
            review_round=current.review_round,
            writer_note="Writer 已执行「去 AI 感」润色。",
        )

    def manual_patch(self, session_id: str, patch: dict) -> DraftVersion:
        if not self.db:
            raise DraftServiceError("Database session required")

        current = self._latest_draft(session_id)
        if not current:
            raise DraftServiceError(f"No draft for session: {session_id}")

        new_data = {
            "title": patch.get("title", current.title),
            "hooks": patch.get("hooks", list(current.hooks)),
            "body": patch.get("body", current.body),
            "tags": patch.get("tags", list(current.tags)),
        }
        return self._save_version(
            session_id,
            new_data,
            review_round=current.review_round,
            writer_note="用户已手动修改文案，Writer 已保存新版本。",
        )

    def _latest_draft(self, session_id: str) -> DraftVersion | None:
        return (
            self.db.query(DraftVersion)
            .filter_by(session_id=session_id)
            .order_by(DraftVersion.version.desc())
            .first()
        )

    def _save_version(
        self,
        session_id: str,
        data: dict,
        *,
        review_round: int,
        writer_note: str,
    ) -> DraftVersion:
        current = self._latest_draft(session_id)
        version = (current.version + 1) if current else 1

        hooks = data.get("hooks") or []
        if isinstance(hooks, str):
            hooks = [hooks]
        tags = data.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]

        draft = DraftVersion(
            session_id=session_id,
            version=version,
            title=(data.get("title") or "").strip(),
            hooks=hooks,
            body=(data.get("body") or "").strip(),
            tags=tags,
            review_round=review_round,
        )
        self.db.add(draft)

        msg = ReviewMessage(
            session_id=session_id,
            phase=ReviewPhase.TEXT.value,
            round=review_round,
            role=MessageRole.WRITER.value,
            content=writer_note,
            attachment={"draft_version": version, "action": writer_note},
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(draft)
        return draft
