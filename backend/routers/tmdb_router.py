import logging
import httpx
from fastapi import APIRouter, HTTPException, Query
from services import tmdb_service

logger = logging.getLogger(__name__)
router = APIRouter()


def _handle_tmdb_error(e: Exception, action: str):
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="TMDB 资源不存在")
        raise HTTPException(status_code=502, detail=f"TMDB 返回错误: {e.response.status_code}")
    logger.error(f"TMDB {action}失败: {e}")
    raise HTTPException(status_code=502, detail="TMDB 服务暂时不可用")


@router.get("/search")
async def search_movies(q: str = Query(...), language: str = "zh-CN"):
    try:
        results = await tmdb_service.search_movies(q, language)
        return {"results": results}
    except Exception as e:
        _handle_tmdb_error(e, "搜索")


@router.get("/movie/{tmdb_id}")
async def get_movie_details(tmdb_id: int):
    try:
        details = await tmdb_service.get_movie_details(tmdb_id)
        return details
    except Exception as e:
        _handle_tmdb_error(e, "获取电影详情")


@router.get("/movie/{tmdb_id}/credits")
async def get_movie_credits(tmdb_id: int):
    try:
        credits = await tmdb_service.get_movie_credits(tmdb_id)
        return credits
    except Exception as e:
        _handle_tmdb_error(e, "获取演职表")


@router.get("/movie/{tmdb_id}/similar")
async def get_similar_movies(tmdb_id: int):
    try:
        results = await tmdb_service.get_similar_movies(tmdb_id)
        return {"results": results}
    except Exception as e:
        _handle_tmdb_error(e, "获取相似电影")
