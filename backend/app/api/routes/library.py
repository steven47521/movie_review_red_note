from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.library import UpdateSessionFlagsRequest
from app.services.library_service import LibraryService, LibraryServiceError

router = APIRouter(prefix="/api/v1", tags=["library"])


@router.get("/sessions")
def list_sessions(
    favorite: bool | None = Query(default=None),
    published: bool | None = Query(default=None),
    status: str | None = Query(default=None),
    movie_title: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    svc = LibraryService(db=db)
    sessions = svc.list_sessions(
        is_favorite=favorite,
        is_published=published,
        status=status,
        movie_title=movie_title,
    )
    return {
        "sessions": [
            {
                "id": s.id,
                "movie_title": s.movie_title,
                "status": s.status,
                "is_favorite": s.is_favorite,
                "is_published": s.is_published,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in sessions
        ],
        "count": len(sessions),
    }


@router.get("/sessions/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    svc = LibraryService(db=db)
    try:
        return svc.get_session_detail(session_id)
    except LibraryServiceError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/timeline")
def get_timeline(session_id: str, db: Session = Depends(get_db)):
    svc = LibraryService(db=db)
    try:
        timeline = svc.get_timeline(session_id)
        return {"session_id": session_id, "timeline": timeline, "count": len(timeline)}
    except LibraryServiceError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    svc = LibraryService(db=db)
    try:
        svc.delete_session(session_id)
        return {"id": session_id, "deleted": True}
    except LibraryServiceError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/sessions/{session_id}")
def update_session_flags(
    session_id: str,
    body: UpdateSessionFlagsRequest,
    db: Session = Depends(get_db),
):
    svc = LibraryService(db=db)
    try:
        session = svc.update_flags(
            session_id,
            is_favorite=body.is_favorite,
            is_published=body.is_published,
        )
        return {
            "id": session.id,
            "is_favorite": session.is_favorite,
            "is_published": session.is_published,
        }
    except LibraryServiceError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc
