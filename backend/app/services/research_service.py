from sqlalchemy.orm import Session

from app.clients.search_client import SearchClient
from app.clients.tmdb_client import TMDBClient, TMDBClientError
from app.models.creation_session import CreationSession, SessionStatus
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot


class ResearchServiceError(Exception):
    pass


class ResearchService:
    def __init__(
        self,
        tmdb_client: TMDBClient | None = None,
        search_client: SearchClient | None = None,
    ):
        self.tmdb = tmdb_client or TMDBClient()
        self.search = search_client or SearchClient()

    @staticmethod
    def _fallback_movie(title: str, year: int | None = None) -> dict:
        """Used when TMDB is unreachable (e.g. network timeout)."""
        return {
            "title": title,
            "year": year,
            "director": None,
            "genres": [],
            "country": None,
            "tmdb_id": None,
            "raw_metadata": {
                "overview": (
                    f"《{title}》是一部值得从主题思想、人物关系与影像语言"
                    "深入讨论的经典影片。"
                ),
                "source": "fallback",
            },
        }

    def research(self, title: str, year: int | None = None) -> dict:
        try:
            movie = self.tmdb.search(title, year=year)
        except TMDBClientError:
            movie = self._fallback_movie(title, year=year)

        opinions = self.search.fetch_opinions(title, movie)
        if len(opinions) < 3:
            raise ResearchServiceError(
                f"Insufficient opinions for '{title}': got {len(opinions)}"
            )

        sources = sorted({o["source"] for o in opinions})
        return {
            "movie": movie,
            "opinions": opinions,
            "sources_summary": ", ".join(sources),
        }

    def research_and_persist(
        self,
        db: Session,
        session_id: str,
        title: str,
        year: int | None = None,
    ) -> dict:
        session = db.get(CreationSession, session_id)
        if not session:
            raise ResearchServiceError(f"Session not found: {session_id}")

        session.status = SessionStatus.RESEARCHING.value
        db.commit()

        result = self.research(title, year=year)

        movie = result["movie"]
        existing_meta = (
            db.query(MovieMeta).filter_by(session_id=session_id).first()
        )
        if existing_meta:
            meta = existing_meta
        else:
            meta = MovieMeta(session_id=session_id, title=movie["title"])
            db.add(meta)

        meta.title = movie["title"]
        meta.year = movie.get("year")
        meta.director = movie.get("director")
        meta.genres = movie.get("genres")
        meta.country = movie.get("country")
        meta.tmdb_id = movie.get("tmdb_id")
        meta.raw_metadata = movie.get("raw_metadata")

        snapshot = ResearchSnapshot(
            session_id=session_id,
            opinions=result["opinions"],
            sources_summary=result.get("sources_summary"),
        )
        db.add(snapshot)

        session.status = SessionStatus.ANGLES_READY.value
        db.commit()
        db.refresh(snapshot)

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
