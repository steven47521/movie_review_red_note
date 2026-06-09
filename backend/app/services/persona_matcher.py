import json
import random
from pathlib import Path

DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "seeds" / "personas.json"

# genre / theme -> preferred MBTI weights (higher = more likely)
GENRE_MBTI_WEIGHTS: dict[str, dict[str, int]] = {
    "Sci-Fi": {"INTJ": 5, "INTP": 5, "INFJ": 4, "ENTJ": 3, "ENTP": 3},
    "Drama": {"INFJ": 5, "INFP": 5, "ENFJ": 4, "ISFJ": 3, "INTJ": 3},
    "Romance": {"ENFP": 5, "INFP": 5, "ESFP": 4, "ISFP": 4, "ENFJ": 3},
    "Crime": {"ISTJ": 5, "ESTJ": 4, "INTJ": 4, "ENTJ": 3, "ISTP": 3},
    "War": {"ISTJ": 5, "ESTJ": 4, "INTJ": 4, "ISTP": 3, "ENTJ": 3},
    "Horror": {"INFJ": 4, "INTP": 4, "ISTP": 4, "ISFP": 3, "ENTP": 3},
    "Comedy": {"ENFP": 5, "ESFP": 5, "ENTP": 4, "ESTP": 3, "ENFJ": 3},
    "Documentary": {"INTJ": 4, "INTP": 4, "ISTJ": 4, "INFJ": 3, "ENTJ": 3},
    "Action": {"ESTP": 5, "ISTP": 4, "ENTJ": 4, "ESTJ": 3, "ESFP": 3},
    "default": {"INFJ": 4, "INTJ": 4, "ENFP": 3, "INFP": 3, "ENTJ": 3},
}

THEME_MBTI_BOOST: dict[str, dict[str, int]] = {
    "existentialism": {"INTJ": 3, "INFJ": 3, "INTP": 2},
    "feminism": {"ENFJ": 3, "INFJ": 3, "INFP": 2},
    "social_critique": {"ENTJ": 3, "ENTP": 3, "INTJ": 2},
    "aesthetics": {"ISFP": 3, "INFP": 3, "INFJ": 2},
    "ethics": {"ISTJ": 3, "INFJ": 3, "INTJ": 2},
}


_SEED_BY_ID: dict[str, dict] | None = None


def get_persona_by_id(persona_id: str | None) -> dict | None:
    if not persona_id:
        return None
    global _SEED_BY_ID
    if _SEED_BY_ID is None:
        matcher = PersonaMatcher()
        _SEED_BY_ID = {persona["id"]: persona for persona in matcher.all_personas()}
    return _SEED_BY_ID.get(persona_id)


class PersonaMatcher:
    def __init__(self, seed_path: str | Path | None = None):
        path = Path(seed_path) if seed_path else DEFAULT_SEED_PATH
        with path.open(encoding="utf-8") as f:
            self._personas: list[dict] = json.load(f)

    def all_personas(self) -> list[dict]:
        return list(self._personas)

    def match_panel(
        self,
        movie: dict,
        angle: dict | None = None,
        *,
        size: int = 4,
        exclude_ids: list[str] | None = None,
        seed: int | None = None,
    ) -> list[dict]:
        angle = angle or {}
        exclude = set(exclude_ids or [])
        candidates = [p for p in self._personas if p["id"] not in exclude]
        if not candidates:
            return []

        weights = self._build_weights(movie, angle)
        rng = random.Random(seed)
        panel_size = max(3, min(5, size))
        selected: list[dict] = []
        used_mbti: set[str] = set()

        scored = sorted(
            candidates,
            key=lambda p: self._score(p, weights, used_mbti, rng),
            reverse=True,
        )

        for persona in scored:
            if len(selected) >= panel_size:
                break
            if persona["mbti"] in used_mbti:
                continue
            selected.append(persona)
            used_mbti.add(persona["mbti"])

        if len(selected) < panel_size:
            for persona in scored:
                if len(selected) >= panel_size:
                    break
                if persona in selected:
                    continue
                selected.append(persona)

        return selected[:panel_size]

    def _build_weights(self, movie: dict, angle: dict) -> dict[str, int]:
        weights: dict[str, int] = {k: v for k, v in GENRE_MBTI_WEIGHTS["default"].items()}

        for genre in movie.get("genres") or []:
            genre_weights = GENRE_MBTI_WEIGHTS.get(genre, {})
            for mbti, w in genre_weights.items():
                weights[mbti] = weights.get(mbti, 0) + w

        theme = (angle.get("theme") or angle.get("title") or "").lower()
        for key, boost in THEME_MBTI_BOOST.items():
            if key in theme:
                for mbti, w in boost.items():
                    weights[mbti] = weights.get(mbti, 0) + w

        year = movie.get("year")
        if year and year < 1980:
            for mbti in ("ISTJ", "INFJ", "INTJ"):
                weights[mbti] = weights.get(mbti, 0) + 1

        return weights

    def _score(
        self,
        persona: dict,
        weights: dict[str, int],
        used_mbti: set[str],
        rng: random.Random,
    ) -> float:
        base = weights.get(persona["mbti"], 1)
        diversity_bonus = 2 if persona["mbti"] not in used_mbti else 0
        age_bonus = {"20s": 0.5, "30s": 0.5, "40s": 1, "50s": 1, "60s+": 1}.get(
            persona["age_band"], 0
        )
        return base + diversity_bonus + age_bonus + rng.random() * 0.1
