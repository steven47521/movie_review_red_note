import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.creation_session import CreationSession
from app.models.draft_version import DraftVersion
from app.models.image_asset import ImageAsset
from app.models.review_message import MessageRole, ReviewMessage
from app.schemas.draft import ManualDraftPatchRequest, RegeneratePartRequest
from app.schemas.images import RegenerateImageRequest
from app.services.draft_service import DraftService, DraftServiceError
from app.services.visual_service import VisualService, VisualServiceError
from app.services.persona_matcher import get_persona_by_id
from app.services.review_orchestrator import (
    ReviewOrchestrator,
    ReviewOrchestratorError,
    ReviewRoundLimitError,
)

router = APIRouter(prefix="/api/v1", tags=["review"])


class UserMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


def _message_payload(message: ReviewMessage) -> dict:
    nickname = None
    mbti = None
    avatar_url = None
    attachment = message.attachment or {}

    if message.role == MessageRole.MODERATOR.value:
        nickname = "主持人"
    elif message.role == MessageRole.WRITER.value:
        nickname = "Writer"
    elif message.role == MessageRole.USER.value:
        nickname = "你"
    elif message.persona:
        nickname = message.persona.nickname
        mbti = message.persona.mbti
        avatar_url = message.persona.avatar_url
    elif message.role == MessageRole.REVIEWER.value:
        seed = get_persona_by_id(message.persona_id)
        if seed:
            nickname = seed.get("nickname")
            mbti = seed.get("mbti")
            avatar_url = seed.get("avatar_url")
        else:
            nickname = attachment.get("nickname") or "审稿人"
            mbti = attachment.get("mbti")
            avatar_url = attachment.get("avatar_url")

    return {
        "id": message.id,
        "phase": message.phase,
        "round": message.round,
        "role": message.role,
        "persona_id": message.persona_id,
        "nickname": nickname,
        "mbti": mbti,
        "avatar_url": avatar_url,
        "content": message.content,
        "scores": message.scores,
        "attachment": message.attachment,
        "created_at": message.created_at.isoformat(),
    }


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/sessions/{session_id}/draft/generate")
def generate_draft(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    orch = ReviewOrchestrator()
    try:
        draft = orch.generate_initial_draft(db, session_id)
        return {
            "session_id": session_id,
            "draft": {
                "version": draft.version,
                "title": draft.title,
                "hooks": draft.hooks,
                "body": draft.body,
                "tags": draft.tags,
            },
        }
    except ReviewOrchestratorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/review/stream")
def review_stream(session_id: str, phase: str = "text", db: Session = Depends(get_db)):
    if phase not in ("text", "image"):
        raise HTTPException(status_code=400, detail="phase must be text or image")

    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    orch = ReviewOrchestrator()

    def event_generator():
        try:
            if phase == "text":
                for item in orch.stream_text_review_round(db, session_id):
                    yield _sse(item["event"], item["data"])
            else:
                orch.run_image_review_round(db, session_id)
                messages = (
                    db.query(ReviewMessage)
                    .filter_by(session_id=session_id, phase="image")
                    .order_by(ReviewMessage.round.desc(), ReviewMessage.created_at)
                    .all()
                )
                latest_round = messages[-1].round if messages else 0
                for m in messages:
                    if m.round != latest_round:
                        continue
                    payload = _message_payload(m)
                    event = "reviewer_message"
                    if m.role == "moderator":
                        event = "moderator_summary"
                    elif m.role == "writer":
                        event = "image_updated"
                    yield _sse(event, payload)
                yield _sse("round_complete", {"round": latest_round, "phase": "image"})
        except ReviewRoundLimitError as exc:
            yield _sse("error", {"message": str(exc)})
        except ReviewOrchestratorError as exc:
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/sessions/{session_id}/review/continue")
def continue_review(
    session_id: str, phase: str = "text", db: Session = Depends(get_db)
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    orch = ReviewOrchestrator()
    try:
        if phase == "image":
            images = orch.run_image_review_round(db, session_id)
            db.refresh(session)
            return {
                "session_id": session_id,
                "phase": "image",
                "round": session.image_review_round,
                "images": [{"id": i.id, "type": i.type, "url": i.url} for i in images],
            }
        draft = orch.run_text_review_round(db, session_id)
        db.refresh(session)
        return {
            "session_id": session_id,
            "phase": "text",
            "round": session.text_review_round,
            "draft_version": draft.version,
        }
    except ReviewRoundLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ReviewOrchestratorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/images/generate")
def generate_images(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = VisualService(db=db)
    try:
        assets = svc.generate_all(session_id)
        return {
            "session_id": session_id,
            "images": [
                {
                    "id": a.id,
                    "type": a.type,
                    "url": a.url,
                    "style_key": a.style_key,
                    "version": a.version,
                }
                for a in assets
            ],
            "count": len(assets),
        }
    except VisualServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/images/regenerate")
def regenerate_image(
    session_id: str, body: RegenerateImageRequest, db: Session = Depends(get_db)
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = VisualService(db=db)
    try:
        asset = svc.regenerate_image(body.image_id, reason=body.reason)
        if asset.session_id != session_id:
            raise HTTPException(status_code=400, detail="Image does not belong to session")
        return {
            "session_id": session_id,
            "image": {
                "id": asset.id,
                "type": asset.type,
                "url": asset.url,
                "version": asset.version,
            },
        }
    except VisualServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/images")
def list_images(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    images = (
        db.query(ImageAsset)
        .filter_by(session_id=session_id)
        .order_by(ImageAsset.type, ImageAsset.version.desc())
        .all()
    )
    latest: dict[str, ImageAsset] = {}
    for img in images:
        if img.type not in latest:
            latest[img.type] = img
    return {
        "session_id": session_id,
        "images": [
            {
                "id": i.id,
                "type": i.type,
                "url": i.url,
                "style_key": i.style_key,
                "version": i.version,
                "review_round": i.review_round,
            }
            for i in latest.values()
        ],
    }


@router.post("/sessions/{session_id}/review/finalize")
def finalize_creation(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    orch = ReviewOrchestrator()
    try:
        updated = orch.finalize(db, session_id)
        return {"session_id": session_id, "status": updated.status}
    except ReviewOrchestratorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/review/finalize-text")
def finalize_text(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    orch = ReviewOrchestrator()
    try:
        updated = orch.finalize_text(db, session_id)
        return {"session_id": session_id, "status": updated.status}
    except ReviewOrchestratorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/review/messages")
def list_review_messages(
    session_id: str, phase: str = "text", db: Session = Depends(get_db)
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if phase not in ("text", "image", "all"):
        raise HTTPException(status_code=400, detail="phase must be text, image, or all")

    query = (
        db.query(ReviewMessage)
        .options(joinedload(ReviewMessage.persona))
        .filter_by(session_id=session_id)
    )
    if phase != "all":
        query = query.filter_by(phase=phase)

    messages = query.order_by(
        ReviewMessage.created_at,
        ReviewMessage.round,
    ).all()

    return {
        "session_id": session_id,
        "messages": [_message_payload(m) for m in messages],
    }


@router.post("/sessions/{session_id}/review/messages")
def create_user_message(
    session_id: str,
    body: UserMessageRequest,
    phase: str = "text",
    db: Session = Depends(get_db),
):
    if phase not in ("text", "image"):
        raise HTTPException(status_code=400, detail="phase must be text or image")

    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    round_num = (
        max(session.text_review_round, 1)
        if phase == "text"
        else max(session.image_review_round, 1)
    )
    message = ReviewMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        phase=phase,
        round=round_num,
        role=MessageRole.USER.value,
        content=body.content.strip(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return _message_payload(message)


@router.post("/sessions/{session_id}/draft/regenerate")
def regenerate_draft_part(
    session_id: str,
    body: RegeneratePartRequest,
    db: Session = Depends(get_db),
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = DraftService(db=db)
    try:
        draft = svc.regenerate_part(session_id, part=body.part)
        return {
            "session_id": session_id,
            "part": body.part,
            "draft": {
                "version": draft.version,
                "title": draft.title,
                "hooks": draft.hooks,
                "body": draft.body,
                "tags": draft.tags,
            },
        }
    except DraftServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/draft/de-ai-polish")
def de_ai_polish_draft(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = DraftService(db=db)
    try:
        draft = svc.apply_de_ai_polish(session_id)
        return {
            "session_id": session_id,
            "draft": {
                "version": draft.version,
                "title": draft.title,
                "hooks": draft.hooks,
                "body": draft.body,
                "tags": draft.tags,
            },
        }
    except DraftServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/sessions/{session_id}/draft")
def patch_draft(
    session_id: str,
    body: ManualDraftPatchRequest,
    db: Session = Depends(get_db),
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = DraftService(db=db)
    patch = body.model_dump(exclude_none=True)
    if not patch:
        raise HTTPException(status_code=400, detail="No fields to update")
    try:
        draft = svc.manual_patch(session_id, patch)
        return {
            "session_id": session_id,
            "draft": {
                "version": draft.version,
                "title": draft.title,
                "hooks": draft.hooks,
                "body": draft.body,
                "tags": draft.tags,
            },
        }
    except DraftServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/draft")
def get_latest_draft(session_id: str, db: Session = Depends(get_db)):
    draft = (
        db.query(DraftVersion)
        .filter_by(session_id=session_id)
        .order_by(DraftVersion.version.desc())
        .first()
    )
    if not draft:
        raise HTTPException(status_code=404, detail="No draft found")
    return {
        "session_id": session_id,
        "version": draft.version,
        "title": draft.title,
        "hooks": draft.hooks,
        "body": draft.body,
        "tags": draft.tags,
        "review_round": draft.review_round,
    }
