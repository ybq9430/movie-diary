from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import MovieUpdate, MovieResponse, MovieListResponse
from services import movie_service
from pydantic import BaseModel, Field

router = APIRouter()


class MovieCreateManual(BaseModel):
    title: str
    year: int | None = None
    genres: list[str] = []
    directors: list[str] = []
    cast: list[str] = []
    regions: list[str] = []
    languages: list[str] = []
    overview: str | None = None
    poster_url: str | None = None
    duration: str | None = None
    user_rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = None
    impressions: str | None = None
    watch_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    is_favorite: bool = False
    tags: list[str] = []


def _movie_to_response(movie) -> MovieResponse:
    tags = getattr(movie, "_tags", [])
    return MovieResponse(
        id=movie.id,
        douban_id=movie.douban_id,
        tmdb_id=movie.tmdb_id,
        title=movie.title,
        original_title=movie.original_title,
        english_title=movie.english_title,
        year=movie.year,
        poster_path=movie.poster_path,
        backdrop_path=movie.backdrop_path,
        overview=movie.overview,
        tmdb_rating=movie.tmdb_rating,
        runtime=movie.runtime,
        release_date=movie.release_date,
        user_rating=movie.user_rating,
        comment=movie.comment,
        impressions=movie.impressions,
        watch_date=movie.watch_date,
        is_favorite=movie.is_favorite or False,
        genres=movie.genres,
        directors=movie.directors,
        cast_=movie.cast_,
        regions=movie.regions,
        languages=movie.languages,
        duration=movie.duration,
        source=movie.source or "douban",
        tags=tags,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
    )


@router.get("", response_model=MovieListResponse)
def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("watch_date"),
    sort_order: str = Query("desc"),
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    region: str | None = None,
    rating_min: int | None = None,
    rating_max: int | None = None,
    search: str | None = None,
    is_favorite: bool | None = None,
    db: Session = Depends(get_db),
):
    result = movie_service.list_movies(
        db, page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order,
        genre=genre, year_from=year_from, year_to=year_to, region=region,
        rating_min=rating_min, rating_max=rating_max, search=search, is_favorite=is_favorite,
    )
    return MovieListResponse(
        items=[_movie_to_response(m) for m in result["items"]],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        pages=result["pages"],
    )


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_service.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return _movie_to_response(movie)


@router.post("", response_model=MovieResponse)
def create_movie(data: MovieCreateManual, db: Session = Depends(get_db)):
    movie = movie_service.create_movie(
        db, title=data.title, year=data.year, genres=data.genres,
        directors=data.directors, cast=data.cast, regions=data.regions,
        languages=data.languages, overview=data.overview, poster_url=data.poster_url,
        duration=data.duration, user_rating=data.user_rating, comment=data.comment,
        impressions=data.impressions, watch_date=data.watch_date, is_favorite=data.is_favorite,
        tags=data.tags,
    )
    return _movie_to_response(movie)


@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, data: MovieUpdate, db: Session = Depends(get_db)):
    movie = movie_service.update_movie(
        db, movie_id, user_rating=data.user_rating, comment=data.comment,
        impressions=data.impressions, watch_date=data.watch_date,
        is_favorite=data.is_favorite, tags=data.tags,
    )
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return _movie_to_response(movie)


@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    if not movie_service.delete_movie(db, movie_id):
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Deleted"}


@router.get("/{movie_id}/similar", response_model=list[MovieResponse])
def get_similar_movies(movie_id: int, db: Session = Depends(get_db)):
    movies = movie_service.get_similar_movies(db, movie_id)
    return [_movie_to_response(m) for m in movies]
