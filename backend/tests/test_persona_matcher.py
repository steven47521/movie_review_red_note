from pathlib import Path

from app.services.persona_matcher import PersonaMatcher

SEED_PATH = Path(__file__).resolve().parent.parent / "app" / "seeds" / "personas.json"


def test_seed_has_80_personas():
    matcher = PersonaMatcher(seed_path=str(SEED_PATH))
    assert len(matcher.all_personas()) == 80


def test_match_panel_returns_3_to_5_personas():
    matcher = PersonaMatcher(seed_path=str(SEED_PATH))
    movie = {"genres": ["Sci-Fi"], "year": 1968, "title": "2001: A Space Odyssey"}
    panel = matcher.match_panel(movie, angle={"theme": "existentialism"})
    assert 3 <= len(panel) <= 5
    mbtis = {p["mbti"] for p in panel}
    assert len(mbtis) >= 2


def test_different_genre_different_panel():
    matcher = PersonaMatcher(seed_path=str(SEED_PATH))
    sci_fi = matcher.match_panel({"genres": ["Sci-Fi"]}, angle={})
    romance = matcher.match_panel({"genres": ["Romance"]}, angle={})
    assert sci_fi[0]["id"] != romance[0]["id"]
