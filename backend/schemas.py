from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# --- Movie Schemas ---
class MovieUpdate(BaseModel):
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    impressions: Optional[str] = None
    watch_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    is_favorite: Optional[bool] = None
    tags: Optional[list[str]] = None


class MovieResponse(BaseModel):
    id: int
    douban_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    title: str
    original_title: Optional[str] = None
    english_title: Optional[str] = None
    year: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    overview: Optional[str] = None
    tmdb_rating: Optional[float] = None
    runtime: Optional[int] = None
    release_date: Optional[str] = None
    user_rating: Optional[int] = None
    comment: Optional[str] = None
    impressions: Optional[str] = None
    watch_date: Optional[str] = None
    is_favorite: bool = False
    genres: Optional[str] = None
    directors: Optional[str] = None
    cast_: Optional[str] = None
    regions: Optional[str] = None
    languages: Optional[str] = None
    duration: Optional[str] = None
    source: str = "douban"
    tags: list[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    items: list[MovieResponse]
    total: int
    page: int
    per_page: int
    pages: int


# --- AI Schemas ---
class PersonalityResponse(BaseModel):
    id: int
    analysis: str
    movie_count: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortraitResponse(BaseModel):
    id: int
    prompt: Optional[str] = None
    image_path: str
    style: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecommendResponse(BaseModel):
    id: int
    movie_title: str
    reason: Optional[str] = None
    tmdb_id: Optional[int] = None
    poster_path: Optional[str] = None
    category: Optional[str] = None
    is_watched: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Import Schemas ---
class ImportStatusResponse(BaseModel):
    status: str
    movie_count: int = 0
    message: str = ""


# --- Stats Schemas ---
class OverviewResponse(BaseModel):
    total_movies: int
    avg_rating: Optional[float] = None
    favorite_genre: Optional[str] = None
    top_directors: list[dict] = []
    time_span: Optional[str] = None
    total_runtime_minutes: Optional[int] = None


class ChartDataResponse(BaseModel):
    labels: list[str]
    values: list[int | float]
    extra: Optional[dict] = None
