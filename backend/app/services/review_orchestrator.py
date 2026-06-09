from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy.orm import Session

from app.llm.client import LLMClient, LLMClientError
from app.llm.prompts.image_reviewer import (
    IMAGE_MODERATOR_SYSTEM,
    IMAGE_REVIEWER_SYSTEM,
    build_image_moderator_user,
    build_image_reviewer_user,
)
from app.llm.prompts.moderator import MODERATOR_SYSTEM, build_moderator_user
from app.llm.prompts.reviewer import REVIEWER_SYSTEM, build_reviewer_user, extract_reviewer_feedback
from app.llm.prompts.writer import (
    DRAFT_SYSTEM,
    REVISION_SYSTEM,
    build_draft_user,
    build_revision_user,
)
from app.models.creation_session import CreationSession, SessionStatus
from app.models.draft_version import DraftVersion
from app.models.image_asset import ImageAsset
from app.models.movie_meta import MovieMeta
from app.models.review_message import MessageRole, ReviewPhase
from app.models.review_message import ReviewMessage
from app.services.persona_matcher import PersonaMatcher
from app.services.visual_service import VisualService


class ReviewRoundLimitError(Exception):
    pass


class ReviewOrchestratorError(Exception):
    pass


REVIEWER_MAX_WORKERS = 5

DEFAULT_PERSONA_LOADER: Callable[[list[str]], list[dict]] | None = None


def _default_persona_loader(ids: list[str]) -> list[dict]:
    matcher = PersonaMatcher()
    by_id = {p["id"]: p for p in matcher.all_personas()}
    return [by_id[i] for i in ids if i in by_id]


class ReviewOrchestrator:
    def __init__(
        self,
        llm_client: LLMClient | None = None,
        max_rounds: int = 5,
        persona_loader: Callable[[list[str]], list[dict]] | None = None,
        visual_service: VisualService | None = None,
        db: Session | None = None,
    ):
        self.llm = llm_client or LLMClient()
        self.max_rounds = max_rounds
        self.persona_loader = persona_loader or _default_persona_loader
        self._visual_service = visual_service
        self._db = db

    def _get_visual_service(self, db: Session) -> VisualService:
        if self._visual_service:
            return self._visual_service
        return VisualService(db=db)

    def ensure_can_continue(self, text_review_round: int) -> None:
        if text_review_round >= self.max_rounds:
            raise ReviewRoundLimitError(
                f"Text review round limit reached ({self.max_rounds})"
            )

    def ensure_can_continue_image(self, image_review_round: int) -> None:
        if image_review_round >= self.max_rounds:
            raise ReviewRoundLimitError(
                f"Image review round limit reached ({self.max_rounds})"
            )

    @staticmethod
    def _persona_attachment(persona: dict, extra: dict | None = None) -> dict:
        payload = {
            "mbti": persona.get("mbti"),
            "nickname": persona.get("nickname"),
            "avatar_url": persona.get("avatar_url"),
        }
        if extra:
            payload.update(extra)
        return payload

    def _reviewer_message_fields(
        self,
        persona: dict,
        result: dict,
        extra: dict | None = None,
    ) -> tuple[str, dict]:
        content, parts = extract_reviewer_feedback(result)
        attachment = self._persona_attachment(persona, {**parts, **(extra or {})})
        return content, attachment

    def _parallel_reviewer_llm_calls(
        self,
        personas: list[dict],
        context: dict,
        *,
        system: str,
        build_user: Callable[[dict, dict], str],
    ) -> list[tuple[dict, dict]]:
        """Call reviewer LLMs in parallel and return results in panel order."""
        if not personas:
            return []

        def _call(persona: dict) -> tuple[dict, dict]:
            try:
                result = self.llm.complete_json(system, build_user(persona, context))
            except LLMClientError as exc:
                raise ReviewOrchestratorError(str(exc)) from exc
            return persona, result

        if len(personas) == 1:
            return [_call(personas[0])]

        by_id: dict[str, tuple[dict, dict]] = {}
        workers = min(len(personas), REVIEWER_MAX_WORKERS)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_call, persona) for persona in personas]
            for future in futures:
                persona, result = future.result()
                by_id[persona["id"]] = (persona, result)

        return [by_id[persona["id"]] for persona in personas]

    def generate_initial_draft(self, db: Session, session_id: str) -> DraftVersion:
        session = db.get(CreationSession, session_id)
        if not session:
            raise ReviewOrchestratorError(f"Session not found: {session_id}")
        if not session.selected_route or not session.selected_angle:
            raise ReviewOrchestratorError("Angle and route must be selected first")

        meta = db.query(MovieMeta).filter_by(session_id=session_id).first()
        movie = {
            "title": meta.title if meta else session.movie_title,
            "year": meta.year if meta else None,
        }

        try:
            data = self.llm.complete_json(
                DRAFT_SYSTEM,
                build_draft_user(movie, session.selected_angle, session.selected_route),
            )
        except LLMClientError as exc:
            raise ReviewOrchestratorError(str(exc)) from exc

        draft = self._save_draft(db, session, data, version=1, review_round=0)
        session.status = SessionStatus.TEXT_REVIEWING.value
        db.commit()
        db.refresh(draft)
        return draft

    def run_text_review_round(self, db: Session, session_id: str) -> DraftVersion:
        session = db.get(CreationSession, session_id)
        if not session:
            raise ReviewOrchestratorError(f"Session not found: {session_id}")

        self.ensure_can_continue(session.text_review_round)
        round_num = session.text_review_round + 1

        draft = self._latest_draft(db, session_id)
        if not draft:
            raise ReviewOrchestratorError("No draft to review")

        panel_ids = session.reviewer_panel_ids or []
        if len(panel_ids) < 3:
            raise ReviewOrchestratorError("Reviewer panel must have at least 3 personas")

        personas = self.persona_loader(panel_ids)[:5]
        draft_dict = self._draft_to_dict(draft)
        reviews: list[dict] = []

        for persona, result in self._parallel_reviewer_llm_calls(
            personas,
            draft_dict,
            system=REVIEWER_SYSTEM,
            build_user=build_reviewer_user,
        ):
            content, attachment = self._reviewer_message_fields(persona, result)
            scores = result.get("scores")
            self._add_message(
                db,
                session_id=session_id,
                phase=ReviewPhase.TEXT.value,
                round_num=round_num,
                role=MessageRole.REVIEWER.value,
                content=content,
                persona_id=persona.get("id"),
                scores=scores,
                attachment=attachment,
            )
            reviews.append({"nickname": persona["nickname"], "content": content})

        try:
            mod = self.llm.complete_json(
                MODERATOR_SYSTEM, build_moderator_user(reviews, draft_dict)
            )
        except LLMClientError as exc:
            raise ReviewOrchestratorError(str(exc)) from exc

        instructions = mod.get("revision_instructions") or ""
        self._add_message(
            db,
            session_id=session_id,
            phase=ReviewPhase.TEXT.value,
            round_num=round_num,
            role=MessageRole.MODERATOR.value,
            content=mod.get("content") or "",
        )

        try:
            revised = self.llm.complete_json(
                REVISION_SYSTEM, build_revision_user(draft_dict, instructions)
            )
        except LLMClientError as exc:
            raise ReviewOrchestratorError(str(exc)) from exc

        next_version = draft.version + 1
        new_draft = self._save_draft(
            db, session, revised, version=next_version, review_round=round_num
        )

        writer_content = revised.get("summary") or "Writer 已发布修改稿。"
        self._add_message(
            db,
            session_id=session_id,
            phase=ReviewPhase.TEXT.value,
            round_num=round_num,
            role=MessageRole.WRITER.value,
            content=writer_content,
            attachment={"draft_version": next_version},
        )

        session.text_review_round = round_num
        session.status = SessionStatus.TEXT_REVIEWING.value
        db.commit()
        db.refresh(new_draft)
        return new_draft

    def finalize_text(self, db: Session, session_id: str) -> CreationSession:
        session = db.get(CreationSession, session_id)
        if not session:
            raise ReviewOrchestratorError(f"Session not found: {session_id}")
        session.status = SessionStatus.TEXT_FINALIZED.value
        db.commit()
        db.refresh(session)
        return session

    def run_image_review_round(self, db: Session, session_id: str) -> list[ImageAsset]:
        session = db.get(CreationSession, session_id)
        if not session:
            raise ReviewOrchestratorError(f"Session not found: {session_id}")

        self.ensure_can_continue_image(session.image_review_round)
        round_num = session.image_review_round + 1

        images = self._latest_images(db, session_id)
        if len(images) < 3:
            raise ReviewOrchestratorError("At least 3 images required for image review")

        draft = self._latest_draft(db, session_id)
        draft_dict = self._draft_to_dict(draft) if draft else {}
        image_dicts = [self._image_to_dict(img) for img in images]

        panel_ids = session.reviewer_panel_ids or []
        personas = self.persona_loader(panel_ids)[:5]
        reviews: list[dict] = []
        image_context = {"images": image_dicts, "draft": draft_dict}

        for persona, result in self._parallel_reviewer_llm_calls(
            personas,
            image_context,
            system=IMAGE_REVIEWER_SYSTEM,
            build_user=lambda persona_item, context: build_image_reviewer_user(
                persona_item, context["images"], context["draft"]
            ),
        ):
            content, attachment = self._reviewer_message_fields(
                persona,
                result,
                {"image_ids": [i["id"] for i in image_dicts]},
            )
            self._add_message(
                db,
                session_id=session_id,
                phase=ReviewPhase.IMAGE.value,
                round_num=round_num,
                role=MessageRole.REVIEWER.value,
                content=content,
                persona_id=persona.get("id"),
                scores=result.get("scores"),
                attachment=attachment,
            )
            reviews.append({"nickname": persona["nickname"], "content": content})

        mod = self.llm.complete_json(
            IMAGE_MODERATOR_SYSTEM,
            build_image_moderator_user(reviews, image_dicts),
        )
        self._add_message(
            db,
            session_id=session_id,
            phase=ReviewPhase.IMAGE.value,
            round_num=round_num,
            role=MessageRole.MODERATOR.value,
            content=mod.get("content") or "",
            attachment={"regenerate_types": mod.get("regenerate_types") or []},
        )

        visual = self._get_visual_service(db)
        regenerated: list[ImageAsset] = []
        for image_type in mod.get("regenerate_types") or []:
            regenerated.extend(
                visual.regenerate_by_types(
                    session_id,
                    [image_type],
                    reason=mod.get("content") or "",
                )
            )

        self._add_message(
            db,
            session_id=session_id,
            phase=ReviewPhase.IMAGE.value,
            round_num=round_num,
            role=MessageRole.WRITER.value,
            content="Visual Agent 已根据配图审稿意见更新图片。",
            attachment={
                "regenerated": [img.id for img in regenerated],
                "types": mod.get("regenerate_types") or [],
                "images": [self._image_to_dict(img) for img in (regenerated or images)],
            },
        )

        session.image_review_round = round_num
        session.status = SessionStatus.IMAGE_REVIEWING.value
        db.commit()
        return regenerated or images

    def finalize(self, db: Session, session_id: str) -> CreationSession:
        session = db.get(CreationSession, session_id)
        if not session:
            raise ReviewOrchestratorError(f"Session not found: {session_id}")
        session.status = SessionStatus.COMPLETED.value
        db.commit()
        db.refresh(session)
        return session

    def stream_text_review_round(
        self, db: Session, session_id: str
    ) -> Iterator[dict]:
        """Yield SSE-style event dicts while running one review round."""
        yield {"event": "round_started", "data": {"session_id": session_id}}

        session = db.get(CreationSession, session_id)
        if not session:
            yield {"event": "error", "data": {"message": "Session not found"}}
            return

        try:
            self.ensure_can_continue(session.text_review_round)
        except ReviewRoundLimitError as exc:
            yield {"event": "error", "data": {"message": str(exc)}}
            return

        if not self._latest_draft(db, session_id):
            try:
                self.generate_initial_draft(db, session_id)
                yield {"event": "draft_created", "data": {"version": 1}}
            except ReviewOrchestratorError as exc:
                yield {"event": "error", "data": {"message": str(exc)}}
                return

        round_num = session.text_review_round + 1
        draft = self._latest_draft(db, session_id)
        draft_dict = self._draft_to_dict(draft)
        personas = self.persona_loader(session.reviewer_panel_ids or [])[:5]
        reviews: list[dict] = []

        def _stream_call(persona: dict) -> tuple[dict, dict]:
            try:
                result = self.llm.complete_json(
                    REVIEWER_SYSTEM, build_reviewer_user(persona, draft_dict)
                )
            except LLMClientError as exc:
                raise ReviewOrchestratorError(str(exc)) from exc
            return persona, result

        workers = min(len(personas), REVIEWER_MAX_WORKERS)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_stream_call, persona): persona for persona in personas}
            for future in as_completed(futures):
                persona, result = future.result()
                content, attachment = self._reviewer_message_fields(persona, result)
                msg = self._add_message(
                    db,
                    session_id=session_id,
                    phase=ReviewPhase.TEXT.value,
                    round_num=round_num,
                    role=MessageRole.REVIEWER.value,
                    content=content,
                    persona_id=persona.get("id"),
                    scores=result.get("scores"),
                    attachment=attachment,
                )
                db.commit()
                reviews.append(
                    {"nickname": persona["nickname"], "content": content}
                )
                yield {
                    "event": "reviewer_message",
                    "data": {
                        "id": msg.id,
                        "role": MessageRole.REVIEWER.value,
                        "persona_id": persona.get("id"),
                        "nickname": persona.get("nickname"),
                        "mbti": persona.get("mbti"),
                        "avatar_url": persona.get("avatar_url"),
                        "content": msg.content,
                        "round": round_num,
                        "attachment": msg.attachment,
                    },
                }

        mod = self.llm.complete_json(
            MODERATOR_SYSTEM, build_moderator_user(reviews, draft_dict)
        )
        mod_msg = self._add_message(
            db,
            session_id=session_id,
            phase=ReviewPhase.TEXT.value,
            round_num=round_num,
            role=MessageRole.MODERATOR.value,
            content=mod.get("content") or "",
        )
        db.commit()
        yield {
            "event": "moderator_summary",
            "data": {"id": mod_msg.id, "content": mod_msg.content, "round": round_num},
        }

        revised = self.llm.complete_json(
            REVISION_SYSTEM,
            build_revision_user(draft_dict, mod.get("revision_instructions") or ""),
        )
        new_draft = self._save_draft(
            db, session, revised, version=draft.version + 1, review_round=round_num
        )
        writer_msg = self._add_message(
            db,
            session_id=session_id,
            phase=ReviewPhase.TEXT.value,
            round_num=round_num,
            role=MessageRole.WRITER.value,
            content=revised.get("summary") or "Writer 已发布修改稿。",
            attachment={"draft_version": new_draft.version},
        )
        session.text_review_round = round_num
        session.status = SessionStatus.TEXT_REVIEWING.value
        db.commit()

        yield {
            "event": "writer_revision",
            "data": {
                "id": writer_msg.id,
                "content": writer_msg.content,
                "draft_version": new_draft.version,
                "round": round_num,
            },
        }
        yield {
            "event": "draft_updated",
            "data": self._draft_to_dict(new_draft),
        }
        yield {"event": "round_complete", "data": {"round": round_num}}

    def _latest_draft(self, db: Session, session_id: str) -> DraftVersion | None:
        return (
            db.query(DraftVersion)
            .filter_by(session_id=session_id)
            .order_by(DraftVersion.version.desc())
            .first()
        )

    def _save_draft(
        self,
        db: Session,
        session: CreationSession,
        data: dict,
        version: int,
        review_round: int,
    ) -> DraftVersion:
        hooks = data.get("hooks") or []
        if isinstance(hooks, str):
            hooks = [hooks]
        tags = data.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]

        draft = DraftVersion(
            session_id=session.id,
            version=version,
            title=(data.get("title") or "").strip() or "未命名标题",
            hooks=hooks,
            body=(data.get("body") or "").strip(),
            tags=tags,
            review_round=review_round,
        )
        db.add(draft)
        return draft

    def _add_message(
        self,
        db: Session,
        *,
        session_id: str,
        phase: str,
        round_num: int,
        role: str,
        content: str,
        persona_id: str | None = None,
        scores: dict | None = None,
        attachment: dict | None = None,
    ) -> ReviewMessage:
        msg = ReviewMessage(
            session_id=session_id,
            phase=phase,
            round=round_num,
            role=role,
            persona_id=persona_id,
            content=content,
            scores=scores,
            attachment=attachment,
        )
        db.add(msg)
        return msg

    def _latest_images(self, db: Session, session_id: str) -> list[ImageAsset]:
        all_images = (
            db.query(ImageAsset)
            .filter_by(session_id=session_id)
            .order_by(ImageAsset.type, ImageAsset.version.desc())
            .all()
        )
        latest_by_type: dict[str, ImageAsset] = {}
        for img in all_images:
            if img.type not in latest_by_type:
                latest_by_type[img.type] = img
        return list(latest_by_type.values())

    @staticmethod
    def _draft_to_dict(draft: DraftVersion) -> dict:
        return {
            "title": draft.title,
            "hooks": draft.hooks,
            "body": draft.body,
            "tags": draft.tags,
            "version": draft.version,
        }

    @staticmethod
    def _image_to_dict(image: ImageAsset) -> dict:
        from app.services.visual_service import IMAGE_TYPE_LABELS

        return {
            "id": image.id,
            "type": image.type,
            "url": image.url,
            "prompt": image.prompt,
            "version": image.version,
            "label": IMAGE_TYPE_LABELS.get(image.type, image.type),
        }
