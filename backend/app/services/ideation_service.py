from sqlalchemy.orm import Session

from app.config import IDEATION_LLM_MODEL, IDEATION_LLM_TIMEOUT
from app.llm.client import LLMClient, LLMClientError
from app.llm.prompts.ideation import (
    ANGLES_SYSTEM,
    ROUTES_SYSTEM,
    build_angles_user,
    build_routes_user,
)
from app.models.creation_session import CreationSession, SessionStatus
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot


class IdeationServiceError(Exception):
    pass


PLOT_KEYWORDS = ("剧情", "故事梗概", "情节梳理", "讲了什么")


class IdeationService:
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    def get_angles_for_session(self, db: Session, session_id: str) -> list[dict]:
        session = db.get(CreationSession, session_id)
        if not session:
            raise IdeationServiceError(f"Session not found: {session_id}")
        if session.angle_candidates:
            return session.angle_candidates
        raise IdeationServiceError("Angles not generated yet")

    def get_routes_for_session(self, db: Session, session_id: str) -> list[dict]:
        session = db.get(CreationSession, session_id)
        if not session:
            raise IdeationServiceError(f"Session not found: {session_id}")
        if session.route_candidates:
            return session.route_candidates
        raise IdeationServiceError("Routes not generated yet")

    def generate_angles(self, movie: dict, opinions: list[dict]) -> list[dict]:
        try:
            data = self.llm.complete_json(
                ANGLES_SYSTEM,
                build_angles_user(movie, opinions),
                model=IDEATION_LLM_MODEL,
                timeout=IDEATION_LLM_TIMEOUT,
            )
        except LLMClientError as exc:
            raise IdeationServiceError(str(exc)) from exc

        angles = data.get("angles") or []
        angles = self._normalize_angles(angles)
        if len(angles) < 3:
            raise IdeationServiceError("LLM returned fewer than 3 angles")
        return angles

    def generate_routes(
        self, movie: dict, angle: dict, opinions: list[dict]
    ) -> list[dict]:
        try:
            data = self.llm.complete_json(
                ROUTES_SYSTEM,
                build_routes_user(movie, angle, opinions),
                model=IDEATION_LLM_MODEL,
                timeout=IDEATION_LLM_TIMEOUT,
            )
        except LLMClientError as exc:
            raise IdeationServiceError(str(exc)) from exc

        routes = data.get("routes") or []
        routes = self._normalize_routes(routes)
        if len(routes) != 2:
            raise IdeationServiceError("LLM must return exactly 2 routes")
        if routes[0].get("outline") == routes[1].get("outline"):
            raise IdeationServiceError("Routes must have distinct outlines")
        return routes

    def generate_angles_for_session(
        self, db: Session, session_id: str, force: bool = False
    ) -> list[dict]:
        session = db.get(CreationSession, session_id)
        if not session:
            raise IdeationServiceError(f"Session not found: {session_id}")
        if session.angle_candidates and not force:
            return session.angle_candidates

        movie, opinions = self._load_research(db, session_id)
        try:
            angles = self.generate_angles(movie, opinions)
        except IdeationServiceError:
            angles = self._fallback_angles(movie)

        session = db.get(CreationSession, session_id)
        if session:
            session.angle_candidates = angles
            session.status = SessionStatus.ANGLES_READY.value
            db.commit()
        return angles

    def select_angle(self, db: Session, session_id: str, angle: dict) -> dict:
        session = db.get(CreationSession, session_id)
        if not session:
            raise IdeationServiceError(f"Session not found: {session_id}")
        session.selected_angle = angle
        db.commit()
        return angle

    def generate_routes_for_session(
        self, db: Session, session_id: str, force: bool = False
    ) -> list[dict]:
        session = db.get(CreationSession, session_id)
        if not session:
            raise IdeationServiceError(f"Session not found: {session_id}")
        if session.route_candidates and not force:
            return session.route_candidates
        if not session.selected_angle:
            raise IdeationServiceError("Select an angle before generating routes")

        movie, opinions = self._load_research(db, session_id)
        try:
            routes = self.generate_routes(movie, session.selected_angle, opinions)
        except IdeationServiceError:
            routes = self._fallback_routes(session.selected_angle)

        session = db.get(CreationSession, session_id)
        if session:
            session.route_candidates = routes
            db.commit()
        return routes

    def select_route(self, db: Session, session_id: str, route: dict) -> dict:
        session = db.get(CreationSession, session_id)
        if not session:
            raise IdeationServiceError(f"Session not found: {session_id}")
        session.selected_route = route
        session.status = SessionStatus.ROUTE_READY.value
        db.commit()
        return route

    def _load_research(self, db: Session, session_id: str) -> tuple[dict, list]:
        meta = db.query(MovieMeta).filter_by(session_id=session_id).first()
        snapshot = (
            db.query(ResearchSnapshot)
            .filter_by(session_id=session_id)
            .order_by(ResearchSnapshot.created_at.desc())
            .first()
        )
        if not meta or not snapshot:
            raise IdeationServiceError("Research must be completed before ideation")

        movie = {
            "title": meta.title,
            "year": meta.year,
            "director": meta.director,
            "genres": meta.genres or [],
        }
        return movie, snapshot.opinions

    def _fallback_angles(self, movie: dict) -> list[dict]:
        title = movie.get("title") or "本片"
        return [
            {
                "id": "a1",
                "title": f"{title}中的人物处境",
                "description": "从主角的选择与代价，看个人与环境的张力。",
            },
            {
                "id": "a2",
                "title": f"{title}的视觉与空间",
                "description": "镜头、色彩与构图如何服务主题，而非单纯好看。",
            },
            {
                "id": "a3",
                "title": f"{title}里的群体关系",
                "description": "人物关系网折射出的社会情绪与价值冲突。",
            },
        ]

    def _fallback_routes(self, angle: dict) -> list[dict]:
        title = angle.get("title") or "主题角度"
        return [
            {
                "id": "r1",
                "title": f"从现象到本质：{title}",
                "outline": [
                    "用一个具体场景或细节开场",
                    "展开论证与例证",
                    "回扣主题并给出观点",
                ],
            },
            {
                "id": "r2",
                "title": f"对照式论述：{title}",
                "outline": [
                    "提出对立观点或常见误解",
                    "用影片细节逐条回应",
                    "总结你的独特读法",
                ],
            },
        ]

    def _normalize_angles(self, angles: list[dict]) -> list[dict]:
        normalized = []
        for i, angle in enumerate(angles):
            title = (angle.get("title") or "").strip()
            description = (angle.get("description") or "").strip()
            if not title or any(k in title for k in PLOT_KEYWORDS):
                continue
            normalized.append(
                {
                    "id": angle.get("id") or f"a{i + 1}",
                    "title": title,
                    "description": description,
                }
            )
        return normalized

    def _normalize_routes(self, routes: list[dict]) -> list[dict]:
        normalized = []
        for i, route in enumerate(routes):
            outline = route.get("outline") or []
            if isinstance(outline, str):
                outline = [outline]
            normalized.append(
                {
                    "id": route.get("id") or f"r{i + 1}",
                    "title": (route.get("title") or f"路线{i + 1}").strip(),
                    "outline": [str(x).strip() for x in outline if str(x).strip()],
                }
            )
        return normalized
