from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.routes import library, personas, review, sessions
from app.config import CORS_ORIGINS, DATABASE_URL
from app.db.session import Base, engine

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def _sqlite_migrate() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        rows = conn.execute(text("PRAGMA table_info(creation_sessions)")).fetchall()
        cols = {row[1] for row in rows}
        if "angle_candidates" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE creation_sessions ADD COLUMN angle_candidates JSON"
                )
            )
        if "route_candidates" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE creation_sessions ADD COLUMN route_candidates JSON"
                )
            )
        conn.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        _sqlite_migrate()
    yield


app = FastAPI(title="RedNote Cinema API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(personas.router)
app.include_router(sessions.router)
app.include_router(library.router)
app.include_router(review.router)

if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}
