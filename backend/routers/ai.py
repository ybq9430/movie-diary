import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Movie, AIPersonality, AIPortrait, AIRecommendation
from schemas import PersonalityResponse, PortraitResponse, RecommendResponse
from services import ai_service, douban_data_service
from utils import parse_json_list

logger = logging.getLogger(__name__)
router = APIRouter()


class PortraitRequest(BaseModel):
    style: str = "水彩"


def _get_movies_data(db: Session) -> list[dict]:
    rows = db.query(
        Movie.title, Movie.year, Movie.genres, Movie.directors,
        Movie.cast_, Movie.regions, Movie.user_rating, Movie.watch_date,
    ).all()
    result = []
    for title, year, genres, directors, cast_, regions, user_rating, watch_date in rows:
        result.append({
            "title": title,
            "year": year,
            "genres": parse_json_list(genres),
            "directors": parse_json_list(directors),
            "cast": parse_json_list(cast_),
            "regions": parse_json_list(regions),
            "user_rating": user_rating,
            "watch_date": watch_date,
        })
    return result


@router.post("/personality", response_model=PersonalityResponse)
async def generate_personality(db: Session = Depends(get_db)):
    movies_data = _get_movies_data(db)
    if len(movies_data) < 5:
        raise HTTPException(status_code=400, detail="需要至少5部电影才能生成分析")

    try:
        analysis = await ai_service.generate_personality(movies_data)
    except Exception as e:
        logger.error(f"AI 性格分析生成失败: {e}")
        raise HTTPException(status_code=502, detail="AI 服务暂时不可用")

    record = AIPersonality(analysis=analysis, movie_count=len(movies_data))
    db.add(record)
    db.commit()
    db.refresh(record)

    return PersonalityResponse(
        id=record.id, analysis=record.analysis,
        movie_count=record.movie_count, created_at=record.created_at,
    )


@router.get("/personality/latest", response_model=PersonalityResponse | None)
def get_latest_personality(db: Session = Depends(get_db)):
    record = db.query(AIPersonality).order_by(AIPersonality.created_at.desc()).first()
    if not record:
        return None
    return PersonalityResponse(
        id=record.id, analysis=record.analysis,
        movie_count=record.movie_count, created_at=record.created_at,
    )


@router.post("/portrait", response_model=PortraitResponse)
async def generate_portrait(body: PortraitRequest, db: Session = Depends(get_db)):
    style = body.style
    movies_data = _get_movies_data(db)
    if len(movies_data) < 5:
        raise HTTPException(status_code=400, detail="需要至少5部电影才能生成肖像")

    try:
        prompt = await ai_service.generate_portrait_prompt(movies_data, style)
    except Exception as e:
        logger.error(f"AI 肖像生成失败: {e}")
        raise HTTPException(status_code=502, detail="AI 服务暂时不可用")

    record = AIPortrait(prompt=prompt, image_path=f"portrait_{style}.txt", style=style)
    db.add(record)
    db.commit()
    db.refresh(record)

    return PortraitResponse(
        id=record.id, prompt=record.prompt,
        image_path=record.image_path, style=record.style, created_at=record.created_at,
    )


@router.get("/portrait/latest", response_model=PortraitResponse | None)
def get_latest_portrait(db: Session = Depends(get_db)):
    record = db.query(AIPortrait).order_by(AIPortrait.created_at.desc()).first()
    if not record:
        return None
    return PortraitResponse(
        id=record.id, prompt=record.prompt,
        image_path=record.image_path, style=record.style, created_at=record.created_at,
    )


@router.get("/portrait/history", response_model=list[PortraitResponse])
def get_portrait_history(db: Session = Depends(get_db)):
    records = db.query(AIPortrait).order_by(AIPortrait.created_at.desc()).all()
    return [
        PortraitResponse(id=r.id, prompt=r.prompt, image_path=r.image_path, style=r.style, created_at=r.created_at)
        for r in records
    ]


@router.post("/recommend", response_model=list[RecommendResponse])
async def generate_recommendations(db: Session = Depends(get_db)):
    movies_data = _get_movies_data(db)
    if len(movies_data) < 5:
        raise HTTPException(status_code=400, detail="需要至少5部电影才能生成推荐")

    try:
        recommendations = await ai_service.generate_recommendations(movies_data)
    except Exception as e:
        logger.error(f"AI 推荐生成失败: {e}")
        raise HTTPException(status_code=502, detail="AI 服务暂时不可用")

    if not recommendations:
        raise HTTPException(status_code=502, detail="AI 未能生成有效推荐，请重试")

    # Save recommendations and try to match poster from local database
    records = []
    for rec in recommendations:
        title = rec.get("title", "")
        reason = rec.get("reason", "")

        poster_path = None
        matched = douban_data_service.search_movie_by_title(db, title)
        if matched and matched.poster_path:
            poster_path = matched.poster_path

        record = AIRecommendation(
            movie_title=title, reason=reason,
            poster_path=poster_path,
            category="AI推荐",
        )
        db.add(record)
        records.append(record)

    db.commit()
    for r in records:
        db.refresh(r)

    return [
        RecommendResponse(
            id=r.id, movie_title=r.movie_title, reason=r.reason,
            tmdb_id=r.tmdb_id, poster_path=r.poster_path,
            category=r.category, is_watched=r.is_watched, created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/recommendations", response_model=list[RecommendResponse])
def get_recommendations(db: Session = Depends(get_db)):
    records = db.query(AIRecommendation).filter(AIRecommendation.is_watched.is_(False)).all()
    return [
        RecommendResponse(
            id=r.id, movie_title=r.movie_title, reason=r.reason,
            tmdb_id=r.tmdb_id, poster_path=r.poster_path,
            category=r.category, is_watched=r.is_watched, created_at=r.created_at,
        )
        for r in records
    ]


@router.put("/recommendations/{rec_id}/watched")
def mark_watched(rec_id: int, db: Session = Depends(get_db)):
    record = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    record.is_watched = True
    db.commit()
    return {"message": "Marked as watched"}
