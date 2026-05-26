import logging
from urllib.parse import urlparse
from collections import OrderedDict
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pathlib import Path
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Startup validation
from config import TMDB_API_KEY, MIMO_API_KEY
if not TMDB_API_KEY:
    logger.warning("TMDB_API_KEY 未设置，TMDB 相关功能将不可用")
if not MIMO_API_KEY:
    logger.warning("MIMO_API_KEY 未设置，AI 相关功能将不可用")

ALLOWED_POSTER_DOMAINS = {"movie.douban.com", "img1.doubanio.com", "img2.doubanio.com", "img3.doubanio.com", "img9.doubanio.com", "img.doubanio.com"}

# In-memory poster cache (URL -> (content, media_type)), max 500 entries
_poster_cache: OrderedDict[str, tuple[bytes, str]] = OrderedDict()
_POSTER_CACHE_MAX = 500

# Shared httpx client for poster proxy (created once, reused)
_http_client = httpx.AsyncClient(
    headers={
        "Referer": "https://movie.douban.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    },
    timeout=10,
    follow_redirects=False,
)

from database import engine, Base
from routers import movies, ai, import_router, stats, tmdb_router, scrape_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Diary", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Routers
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(import_router.router, prefix="/api/import", tags=["import"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(tmdb_router.router, prefix="/api/tmdb", tags=["tmdb"])
app.include_router(scrape_router.router, prefix="/api/scrape", tags=["scrape"])


@app.get("/api/poster")
async def proxy_poster(url: str = Query(...)):
    """代理豆瓣海报图片，绕过防盗链，带内存缓存"""
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_POSTER_DOMAINS:
        raise HTTPException(status_code=403, detail="不允许的域名")

    # Check cache
    if url in _poster_cache:
        content, media_type = _poster_cache[url]
        _poster_cache.move_to_end(url)
        return Response(content=content, media_type=media_type, headers={"Cache-Control": "public, max-age=86400"})

    try:
        resp = await _http_client.get(url)
        if resp.status_code == 200:
            media_type = resp.headers.get("content-type", "image/jpeg")
            # Evict oldest if cache full
            if len(_poster_cache) >= _POSTER_CACHE_MAX:
                _poster_cache.popitem(last=False)
            _poster_cache[url] = (resp.content, media_type)
            return Response(content=resp.content, media_type=media_type, headers={"Cache-Control": "public, max-age=86400"})
    except httpx.RequestError as e:
        logger.warning(f"海报代理请求失败: {e}")
    return Response(status_code=404)


@app.on_event("shutdown")
async def shutdown():
    await _http_client.aclose()
    from services import tmdb_service, ai_service
    await tmdb_service.close()
    await ai_service.close()


@app.get("/")
def root():
    return {"message": "Movie Diary API", "version": "1.0.0"}
