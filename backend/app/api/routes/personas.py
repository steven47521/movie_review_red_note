from fastapi import APIRouter

from app.services.persona_matcher import PersonaMatcher

router = APIRouter(prefix="/api/v1", tags=["personas"])


@router.get("/personas")
def list_personas():
    matcher = PersonaMatcher()
    return {"personas": matcher.all_personas(), "count": len(matcher.all_personas())}
