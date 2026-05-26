import httpx
from config import TMDB_API_KEY, TMDB_BASE_URL

_client = httpx.AsyncClient(timeout=10)


async def close():
    await _client.aclose()


async def search_movies(query: str, language: str = "zh-CN") -> list[dict]:
    resp = await _client.get(
        f"{TMDB_BASE_URL}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": query, "language": language},
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


async def get_movie_details(tmdb_id: int, language: str = "zh-CN") -> dict:
    resp = await _client.get(
        f"{TMDB_BASE_URL}/movie/{tmdb_id}",
        params={"api_key": TMDB_API_KEY, "language": language},
    )
    resp.raise_for_status()
    return resp.json()


async def get_movie_credits(tmdb_id: int, language: str = "zh-CN") -> dict:
    resp = await _client.get(
        f"{TMDB_BASE_URL}/movie/{tmdb_id}/credits",
        params={"api_key": TMDB_API_KEY, "language": language},
    )
    resp.raise_for_status()
    return resp.json()


async def get_similar_movies(tmdb_id: int, language: str = "zh-CN") -> list[dict]:
    resp = await _client.get(
        f"{TMDB_BASE_URL}/movie/{tmdb_id}/similar",
        params={"api_key": TMDB_API_KEY, "language": language},
    )
    resp.raise_for_status()
    return resp.json().get("results", [])
