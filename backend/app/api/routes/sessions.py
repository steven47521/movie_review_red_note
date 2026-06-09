from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.creation_session import CreationSession
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot
from app.schemas.ideation import SelectAngleRequest, SelectRouteRequest
from app.schemas.sessions import CreateSessionRequest
from app.services.ideation_service import IdeationService, IdeationServiceError
from app.services.persona_matcher import PersonaMatcher
from app.services.research_service import ResearchService, ResearchServiceError

router = APIRouter(prefix="/api/v1", tags=["sessions"])


def _movie_context(db: Session, session: CreationSession) -> dict:
    meta = db.query(MovieMeta).filter_by(session_id=session.id).first()
    if meta:
        return {
            "title": meta.title,
            "year": meta.year,
            "genres": meta.genres or [],
        }
    return {"title": session.movie_title, "genres": []}


@router.post("/sessions")
def create_session(body: CreateSessionRequest, db: Session = Depends(get_db)):
    session = CreationSession(movie_title=body.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "movie_title": session.movie_title,
        "status": session.status,
        "year": body.year,
    }


@router.post("/sessions/{session_id}/research")
def trigger_research(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    svc = ResearchService()
    try:
        return svc.research_and_persist(db, session_id, session.movie_title)
    except ResearchServiceError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/research")
def get_research(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    meta = db.query(MovieMeta).filter_by(session_id=session_id).first()
    snapshot = (
        db.query(ResearchSnapshot)
        .filter_by(session_id=session_id)
        .order_by(ResearchSnapshot.created_at.desc())
        .first()
    )
    if not meta or not snapshot:
        raise HTTPException(status_code=404, detail="Research not completed yet")

    return {
        "session_id": session_id,
        "movie": {
            "title": meta.title,
            "year": meta.year,
            "director": meta.director,
            "genres": meta.genres,
            "country": meta.country,
            "tmdb_id": meta.tmdb_id,
        },
        "opinions": snapshot.opinions,
        "sources_summary": snapshot.sources_summary,
        "snapshot_id": snapshot.id,
    }


@router.get("/sessions/{session_id}/angles")
def get_angles(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = IdeationService()
    try:
        angles = svc.get_angles_for_session(db, session_id)
        return {"session_id": session_id, "angles": angles, "count": len(angles)}
    except IdeationServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/angles/generate")
def generate_angles(
    session_id: str,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = IdeationService()
    try:
        angles = svc.generate_angles_for_session(db, session_id, force=force)
        return {"session_id": session_id, "angles": angles, "count": len(angles)}
    except IdeationServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/angles/select")
def select_angle(
    session_id: str, body: SelectAngleRequest, db: Session = Depends(get_db)
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = IdeationService()
    angle = {
        "id": body.angle_id,
        "title": body.title,
        "description": body.description,
    }
    try:
        selected = svc.select_angle(db, session_id, angle)
        return {"session_id": session_id, "selected_angle": selected}
    except IdeationServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/routes")
def get_routes(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = IdeationService()
    try:
        routes = svc.get_routes_for_session(db, session_id)
        return {"session_id": session_id, "routes": routes, "count": len(routes)}
    except IdeationServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/routes/generate")
def generate_routes(
    session_id: str,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = IdeationService()
    try:
        routes = svc.generate_routes_for_session(db, session_id, force=force)
        return {"session_id": session_id, "routes": routes, "count": len(routes)}
    except IdeationServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/routes/select")
def select_route(
    session_id: str, body: SelectRouteRequest, db: Session = Depends(get_db)
):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    svc = IdeationService()
    route = {
        "id": body.route_id,
        "title": body.title,
        "outline": body.outline,
    }
    try:
        selected = svc.select_route(db, session_id, route)
        return {"session_id": session_id, "selected_route": selected}
    except IdeationServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/reviewers/match")
def match_reviewers(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    matcher = PersonaMatcher()
    movie = _movie_context(db, session)
    angle = session.selected_angle or {}
    panel = matcher.match_panel(movie, angle=angle)
    session.reviewer_panel_ids = [p["id"] for p in panel]
    db.commit()

    return {"session_id": session_id, "panel": panel, "count": len(panel)}


@router.post("/sessions/{session_id}/reviewers/reshuffle")
def reshuffle_reviewers(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CreationSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    matcher = PersonaMatcher()
    movie = _movie_context(db, session)
    angle = session.selected_angle or {}
    exclude = session.reviewer_panel_ids or []
    panel = matcher.match_panel(movie, angle=angle, exclude_ids=exclude)
    session.reviewer_panel_ids = [p["id"] for p in panel]
    db.commit()

    return {"session_id": session_id, "panel": panel, "count": len(panel)}
