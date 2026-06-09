from unittest.mock import patch

from app.clients.search_client import SearchClient


def test_fetch_opinions_always_returns_at_least_three():
    client = SearchClient()
    movie = {
        "title": "廊桥遗梦",
        "year": 1995,
        "raw_metadata": {"overview": "简短介绍。"},
    }

    with patch.object(client, "_opinions_from_llm_search", return_value=[]):
        opinions = client.fetch_opinions("廊桥遗梦", movie)

    assert len(opinions) >= 3
    assert all("text" in item and "source" in item for item in opinions)
