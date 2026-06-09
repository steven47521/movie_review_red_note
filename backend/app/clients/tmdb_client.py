import httpx

from app.config import TMDB_API_KEY

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_TIMEOUT = 15.0
GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Sci-Fi",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}


class TMDBClientError(Exception):
    pass


class TMDBClient:
    def __init__(self, api_key: str | None = None, timeout: float = 30.0):
        self.api_key = api_key or TMDB_API_KEY
        self.timeout = timeout

    def search(self, title: str, year: int | None = None) -> dict:
        if not self.api_key:
            raise TMDBClientError("TMDB_API_KEY is not configured")

        params = {"api_key": self.api_key, "query": title, "language": "zh-CN"}
        if year:
            params["year"] = year

        try:
            with httpx.Client(timeout=min(self.timeout, TMDB_TIMEOUT)) as client:
                search_resp = client.get(f"{TMDB_BASE}/search/movie", params=params)
                search_resp.raise_for_status()
                results = search_resp.json().get("results") or []
                if not results:
                    raise TMDBClientError(f"Movie not found: {title}")

                movie = results[0]
                movie_id = movie["id"]
                detail_resp = client.get(
                    f"{TMDB_BASE}/movie/{movie_id}",
                    params={
                        "api_key": self.api_key,
                        "language": "zh-CN",
                        "append_to_response": "credits",
                    },
                )
                detail_resp.raise_for_status()
                detail = detail_resp.json()
        except httpx.HTTPError as exc:
            raise TMDBClientError(f"TMDB request failed: {exc}") from exc

        director = self._extract_director(detail)
        genres = [
            GENRE_MAP.get(g["id"], g["name"])
            for g in detail.get("genres") or []
        ]
        release_year = None
        if detail.get("release_date"):
            release_year = int(detail["release_date"][:4])

        countries = detail.get("production_countries") or []
        country = countries[0]["name"] if countries else None

        return {
            "title": detail.get("title") or detail.get("original_title") or title,
            "year": release_year or year,
            "director": director,
            "genres": genres,
            "country": country,
            "tmdb_id": movie_id,
            "raw_metadata": {
                "overview": detail.get("overview"),
                "vote_average": detail.get("vote_average"),
                "tagline": detail.get("tagline"),
            },
        }

    @staticmethod
    def _extract_director(detail: dict) -> str | None:
        for crew in detail.get("credits", {}).get("crew") or []:
            if crew.get("job") == "Director":
                return crew.get("name")
        return None
