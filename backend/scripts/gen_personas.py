"""One-off script to generate personas.json. Run: python scripts/gen_personas.py"""
import json
import uuid
from pathlib import Path

MBTI = [
    "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP",
]
AGES = ["20s", "30s", "40s", "50s", "60s+"]
TASTE = {
    "INTJ": {"focus": "structure", "tone": "analytical"},
    "INTP": {"focus": "ideas", "tone": "curious"},
    "ENTJ": {"focus": "argument", "tone": "direct"},
    "ENTP": {"focus": "debate", "tone": "witty"},
    "INFJ": {"focus": "meaning", "tone": "empathetic"},
    "INFP": {"focus": "values", "tone": "poetic"},
    "ENFJ": {"focus": "resonance", "tone": "warm"},
    "ENFP": {"focus": "emotion", "tone": "energetic"},
    "ISTJ": {"focus": "craft", "tone": "precise"},
    "ISFJ": {"focus": "character", "tone": "gentle"},
    "ESTJ": {"focus": "clarity", "tone": "firm"},
    "ESFJ": {"focus": "audience", "tone": "friendly"},
    "ISTP": {"focus": "visuals", "tone": "cool"},
    "ISFP": {"focus": "aesthetics", "tone": "sensitive"},
    "ESTP": {"focus": "punch", "tone": "bold"},
    "ESFP": {"focus": "vibe", "tone": "playful"},
}

personas = []
for mbti in MBTI:
    for age in AGES:
        age_slug = age.replace("+", "plus")
        personas.append({
            "id": str(uuid.uuid4()),
            "mbti": mbti,
            "age_band": age,
            "nickname": f"{mbti}影评人·{age}",
            "avatar_url": f"/avatars/{mbti.lower()}_{age_slug}.png",
            "taste_profile": {**TASTE[mbti], "age_band": age, "mbti": mbti},
        })

out = Path(__file__).resolve().parent.parent / "app" / "seeds" / "personas.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(personas, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {len(personas)} personas to {out}")
