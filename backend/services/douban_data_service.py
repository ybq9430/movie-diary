from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Movie
from utils import parse_json_list


def search_movie_by_title(db: Session, title: str, year: int | None = None) -> Movie | None:
    """在本地数据库中搜索电影"""
    movie = db.query(Movie).filter(Movie.title == title).first()
    if movie:
        return movie
    # 模糊匹配
    movie = db.query(Movie).filter(Movie.title.contains(title)).first()
    if movie and year and movie.year:
        if abs(movie.year - year) <= 1:
            return movie
        return None  # Year mismatch — don't return wrong movie
    return movie


def get_similar_movies(db: Session, movie_id: int, limit: int = 12) -> list[Movie]:
    """基于类型/导演/地区的本地相似度算法"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return []

    target_genres = parse_json_list(movie.genres)
    target_directors = parse_json_list(movie.directors)
    target_regions = parse_json_list(movie.regions)

    # SQL pre-filter: only load movies that share at least one genre, director, or region
    filters = []
    for g in target_genres:
        filters.append(Movie.genres.contains(g))
    for d in target_directors:
        filters.append(Movie.directors.contains(d))
    for r in target_regions:
        filters.append(Movie.regions.contains(r))
    if movie.year:
        filters.append(Movie.year.between(movie.year - 5, movie.year + 5))

    if not filters:
        return []

    candidates = db.query(Movie).filter(Movie.id != movie_id, or_(*filters)).all()

    target_genres_set = set(target_genres)
    target_directors_set = set(target_directors)
    target_regions_set = set(target_regions)
    scored = []

    for m in candidates:
        score = 0
        m_genres = set(parse_json_list(m.genres))
        m_directors = set(parse_json_list(m.directors))
        m_regions = set(parse_json_list(m.regions))

        score += len(target_genres_set & m_genres) * 2
        score += len(target_directors_set & m_directors) * 3
        score += len(target_regions_set & m_regions) * 1
        if movie.year and m.year and abs(movie.year - m.year) <= 5:
            score += 1

        if score > 0:
            scored.append((score, m))

    scored.sort(key=lambda x: -x[0])
    return [m for _, m in scored[:limit]]
