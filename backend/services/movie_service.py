import json
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Movie, MovieTag
from services import douban_data_service


def list_movies(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    sort_by: str = "watch_date",
    sort_order: str = "desc",
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    region: str | None = None,
    rating_min: int | None = None,
    rating_max: int | None = None,
    search: str | None = None,
    is_favorite: bool | None = None,
) -> dict:
    query = db.query(Movie)

    # Filters
    if search:
        query = query.filter(
            or_(
                Movie.title.contains(search),
                Movie.original_title.contains(search),
                Movie.english_title.contains(search),
            )
        )
    if genre:
        query = query.filter(Movie.genres.contains(genre))
    if year_from is not None:
        query = query.filter(Movie.year >= year_from)
    if year_to is not None:
        query = query.filter(Movie.year <= year_to)
    if region:
        query = query.filter(Movie.regions.contains(region))
    if rating_min is not None:
        query = query.filter(Movie.user_rating >= rating_min)
    if rating_max is not None:
        query = query.filter(Movie.user_rating <= rating_max)
    if is_favorite is not None:
        query = query.filter(Movie.is_favorite == is_favorite)

    # Sorting — allowlist of exposed columns
    ALLOWED_SORT_COLUMNS = {"watch_date", "title", "year", "user_rating", "created_at", "duration"}
    sort_col = getattr(Movie, sort_by, None)
    if sort_col is None or sort_by not in ALLOWED_SORT_COLUMNS:
        sort_col = Movie.watch_date
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    total = query.count()
    pages = (total + per_page - 1) // per_page
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    # Batch load tags for all items in one query
    if items:
        movie_ids = [item.id for item in items]
        tag_rows = db.query(MovieTag).filter(MovieTag.movie_id.in_(movie_ids)).all()
        tags_by_movie = defaultdict(list)
        for t in tag_rows:
            tags_by_movie[t.movie_id].append(t.tag)
        for item in items:
            item._tags = tags_by_movie.get(item.id, [])

    return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}


def get_movie(db: Session, movie_id: int) -> Movie | None:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        tags = db.query(MovieTag).filter(MovieTag.movie_id == movie.id).all()
        movie._tags = [t.tag for t in tags]
    return movie


def create_movie(db: Session, title: str, **kwargs) -> Movie:
    """手动添加电影（不需要 TMDB）"""
    movie = Movie(
        title=title,
        year=kwargs.get("year"),
        genres=json.dumps(kwargs.get("genres", []), ensure_ascii=False),
        directors=json.dumps(kwargs.get("directors", []), ensure_ascii=False),
        cast_=json.dumps(kwargs.get("cast", []), ensure_ascii=False),
        regions=json.dumps(kwargs.get("regions", []), ensure_ascii=False),
        languages=json.dumps(kwargs.get("languages", []), ensure_ascii=False),
        overview=kwargs.get("overview"),
        poster_path=kwargs.get("poster_url"),
        duration=kwargs.get("duration"),
        source="manual",
        user_rating=kwargs.get("user_rating"),
        comment=kwargs.get("comment"),
        impressions=kwargs.get("impressions"),
        watch_date=kwargs.get("watch_date"),
        is_favorite=kwargs.get("is_favorite", False),
    )
    db.add(movie)
    db.flush()  # get movie.id without committing

    tags = kwargs.get("tags", [])
    for tag in tags:
        db.add(MovieTag(movie_id=movie.id, tag=tag))

    db.commit()
    db.refresh(movie)
    movie._tags = tags
    return movie


def update_movie(db: Session, movie_id: int, **kwargs) -> Movie | None:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return None

    for key, value in kwargs.items():
        if key == "tags":
            if value is not None:
                db.query(MovieTag).filter(MovieTag.movie_id == movie_id).delete()
                for tag in value:
                    db.add(MovieTag(movie_id=movie_id, tag=tag))
        elif hasattr(movie, key) and value is not None:
            setattr(movie, key, value)

    db.commit()
    db.refresh(movie)
    tags = db.query(MovieTag).filter(MovieTag.movie_id == movie.id).all()
    movie._tags = [t.tag for t in tags]
    return movie


def delete_movie(db: Session, movie_id: int) -> bool:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return False
    db.delete(movie)
    db.commit()
    return True


def get_similar_movies(db: Session, movie_id: int) -> list[Movie]:
    """获取相似电影（基于类型/导演/地区）"""
    return douban_data_service.get_similar_movies(db, movie_id)
