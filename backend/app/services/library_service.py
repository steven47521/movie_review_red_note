from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.creation_session import CreationSession
from app.models.draft_version import DraftVersion
from app.models.image_asset import ImageAsset
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot
from app.models.review_message import ReviewMessage


class LibraryServiceError(Exception):
    pass


class LibraryService:
    def __init__(self, db: Session | None = None):
        self.db = db

    def list_sessions(
        self,
        is_favorite: bool | None = None,
        is_published: bool | None = None,
        status: str | None = None,
        movie_title: str | None = None,
    ) -> list[CreationSession]:
        if not self.db:
            raise LibraryServiceError("Database session required")

        query = self.db.query(CreationSession)
        if is_favorite is not None:
            query = query.filter(CreationSession.is_favorite == is_favorite)
        if is_published is not None:
            query = query.filter(CreationSession.is_published == is_published)
        if status:
            query = query.filter(CreationSession.status == status)
        if movie_title:
            query = query.filter(CreationSession.movie_title.contains(movie_title))

        return query.order_by(CreationSession.created_at.desc()).all()

    def get_session_detail(self, session_id: str) -> dict:
        if not self.db:
            raise LibraryServiceError("Database session required")

        session = self.db.get(CreationSession, session_id)
        if not session:
            raise LibraryServiceError(f"Session not found: {session_id}")

        meta = self.db.query(MovieMeta).filter_by(session_id=session_id).first()
        movie = None
        if meta:
            movie = {
                "title": meta.title,
                "year": meta.year,
                "director": meta.director,
                "genres": meta.genres or [],
                "country": meta.country,
                "tmdb_id": meta.tmdb_id,
            }

        return {
            "id": session.id,
            "movie_title": session.movie_title,
            "status": session.status,
            "selected_angle": session.selected_angle,
            "selected_route": session.selected_route,
            "text_review_round": session.text_review_round,
            "image_review_round": session.image_review_round,
            "is_favorite": session.is_favorite,
            "is_published": session.is_published,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "movie": movie,
        }

    def get_timeline(self, session_id: str) -> list[dict]:
        if not self.db:
            raise LibraryServiceError("Database session required")

        session = self.db.get(CreationSession, session_id)
        if not session:
            raise LibraryServiceError(f"Session not found: {session_id}")

        events: list[dict] = []

        events.append(
            {
                "type": "session_created",
                "timestamp": _iso(session.created_at),
                "id": session.id,
                "data": {
                    "movie_title": session.movie_title,
                    "status": session.status,
                },
            }
        )

        snapshots = (
            self.db.query(ResearchSnapshot)
            .filter_by(session_id=session_id)
            .order_by(ResearchSnapshot.created_at.asc())
            .all()
        )
        for snapshot in snapshots:
            events.append(
                {
                    "type": "research",
                    "timestamp": _iso(snapshot.created_at),
                    "id": snapshot.id,
                    "data": {
                        "opinions": snapshot.opinions,
                        "sources_summary": snapshot.sources_summary,
                    },
                }
            )

        if session.selected_angle:
            events.append(
                {
                    "type": "angle_selected",
                    "timestamp": _iso(session.updated_at),
                    "id": session.id,
                    "data": session.selected_angle,
                }
            )

        if session.selected_route:
            events.append(
                {
                    "type": "route_selected",
                    "timestamp": _iso(session.updated_at),
                    "id": session.id,
                    "data": session.selected_route,
                }
            )

        messages = (
            self.db.query(ReviewMessage)
            .filter_by(session_id=session_id)
            .order_by(ReviewMessage.created_at.asc())
            .all()
        )
        for message in messages:
            events.append(
                {
                    "type": "review_message",
                    "timestamp": _iso(message.created_at),
                    "id": message.id,
                    "data": {
                        "phase": message.phase,
                        "round": message.round,
                        "role": message.role,
                        "persona_id": message.persona_id,
                        "content": message.content,
                        "scores": message.scores,
                        "attachment": message.attachment,
                    },
                }
            )

        drafts = (
            self.db.query(DraftVersion)
            .filter_by(session_id=session_id)
            .order_by(DraftVersion.created_at.asc())
            .all()
        )
        for draft in drafts:
            events.append(
                {
                    "type": "draft_version",
                    "timestamp": _iso(draft.created_at),
                    "id": draft.id,
                    "data": {
                        "version": draft.version,
                        "title": draft.title,
                        "hooks": draft.hooks,
                        "body": draft.body,
                        "tags": draft.tags,
                        "review_round": draft.review_round,
                    },
                }
            )

        images = (
            self.db.query(ImageAsset)
            .filter_by(session_id=session_id)
            .order_by(ImageAsset.created_at.asc())
            .all()
        )
        for image in images:
            events.append(
                {
                    "type": "image_asset",
                    "timestamp": _iso(image.created_at),
                    "id": image.id,
                    "data": {
                        "type": image.type,
                        "url": image.url,
                        "prompt": image.prompt,
                        "style_key": image.style_key,
                        "version": image.version,
                        "review_round": image.review_round,
                    },
                }
            )

        events.sort(key=lambda event: event["timestamp"])
        return events

    def update_flags(
        self,
        session_id: str,
        is_favorite: bool | None = None,
        is_published: bool | None = None,
    ) -> CreationSession:
        if not self.db:
            raise LibraryServiceError("Database session required")

        session = self.db.get(CreationSession, session_id)
        if not session:
            raise LibraryServiceError(f"Session not found: {session_id}")

        if is_favorite is not None:
            session.is_favorite = is_favorite
        if is_published is not None:
            session.is_published = is_published

        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session_id: str) -> None:
        if not self.db:
            raise LibraryServiceError("Database session required")

        session = self.db.get(CreationSession, session_id)
        if not session:
            raise LibraryServiceError(f"Session not found: {session_id}")

        self.db.query(ReviewMessage).filter_by(session_id=session_id).delete()
        self.db.query(DraftVersion).filter_by(session_id=session_id).delete()
        self.db.query(ImageAsset).filter_by(session_id=session_id).delete()
        self.db.query(ResearchSnapshot).filter_by(session_id=session_id).delete()
        self.db.query(MovieMeta).filter_by(session_id=session_id).delete()
        self.db.query(AuditLog).filter_by(session_id=session_id).delete()
        self.db.delete(session)
        self.db.commit()


def _iso(value: datetime) -> str:
    return value.isoformat()
