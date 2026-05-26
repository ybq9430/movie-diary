import re
from collections import Counter
from sqlalchemy.orm import Session
from models import Movie
from utils import parse_json_list as _parse_json_list


def get_overview(db: Session) -> dict:
    from sqlalchemy import func

    total = db.query(func.count(Movie.id)).scalar()
    if not total:
        return {"total_movies": 0}

    # Single query for SQL-aggregable fields
    row = db.query(
        func.avg(Movie.user_rating),
        func.min(Movie.watch_date),
        func.max(Movie.watch_date),
    ).filter(
        Movie.user_rating.isnot(None),
        Movie.watch_date.isnot(None),
    ).first()

    avg_rating = round(row[0], 1) if row and row[0] else None
    min_date, max_date = (row[1], row[2]) if row else (None, None)
    time_span = f"{min_date} ~ {max_date}" if min_date and max_date and min_date != max_date else None

    # Single query for JSON-parseable columns (directors, genres, duration)
    all_directors = []
    all_genres = []
    total_minutes = 0
    for directors, genres, duration in db.query(
        Movie.directors, Movie.genres, Movie.duration
    ).all():
        if directors:
            all_directors.extend(_parse_json_list(directors))
        if genres:
            all_genres.extend(_parse_json_list(genres))
        if duration:
            match = re.search(r"(\d+)", duration)
            if match:
                total_minutes += int(match.group(1))

    top_dirs = [{"name": d, "count": c} for d, c in Counter(all_directors).most_common(5)]
    fav_genre = Counter(all_genres).most_common(1)[0][0] if all_genres else None

    return {
        "total_movies": total,
        "avg_rating": avg_rating,
        "favorite_genre": fav_genre,
        "top_directors": top_dirs,
        "time_span": time_span,
        "total_runtime_minutes": total_minutes if total_minutes > 0 else None,
    }


def get_rating_distribution(db: Session) -> dict:
    from sqlalchemy import func
    rows = (
        db.query(Movie.user_rating, func.count())
        .filter(Movie.user_rating.isnot(None))
        .group_by(Movie.user_rating)
        .all()
    )
    counts = {r: c for r, c in rows}
    labels = ["1星", "2星", "3星", "4星", "5星"]
    values = [counts.get(i, 0) for i in range(1, 6)]
    return {"labels": labels, "values": values}


def get_genre_preference(db: Session) -> dict:
    all_genres = []
    for (g,) in db.query(Movie.genres).filter(Movie.genres.isnot(None)).all():
        all_genres.extend(_parse_json_list(g))
    top = Counter(all_genres).most_common(10)
    return {"labels": [g for g, _ in top], "values": [c for _, c in top]}


def get_watching_trend(db: Session) -> dict:
    from sqlalchemy import func
    col = func.substr(Movie.watch_date, 1, 7)
    rows = (
        db.query(col, func.count())
        .filter(Movie.watch_date.isnot(None))
        .group_by(col)
        .order_by(col)
        .all()
    )
    return {"labels": [r[0] for r in rows], "values": [r[1] for r in rows]}


def get_director_ranking(db: Session) -> dict:
    all_directors = []
    for (d,) in db.query(Movie.directors).filter(Movie.directors.isnot(None)).all():
        all_directors.extend(_parse_json_list(d))
    top = Counter(all_directors).most_common(15)
    return {"labels": [d for d, _ in top], "values": [c for _, c in top]}


def get_region_distribution(db: Session) -> dict:
    all_regions = []
    for (r,) in db.query(Movie.regions).filter(Movie.regions.isnot(None)).all():
        all_regions.extend(_parse_json_list(r))
    top = Counter(all_regions).most_common(10)
    return {"labels": [r for r, _ in top], "values": [c for _, c in top]}


def get_monthly_pattern(db: Session) -> dict:
    from sqlalchemy import func, cast, Integer
    col = cast(func.substr(Movie.watch_date, 6, 2), Integer)
    rows = (
        db.query(col, func.count())
        .filter(Movie.watch_date.isnot(None))
        .group_by(col)
        .all()
    )
    month_counts = {r: c for r, c in rows}
    labels = [f"{i}月" for i in range(1, 13)]
    values = [month_counts.get(i, 0) for i in range(1, 13)]
    return {"labels": labels, "values": values}


def get_year_distribution(db: Session) -> dict:
    from sqlalchemy import func, literal_column
    # Use (year - year % 10) instead of (year / 10 * 10) for SQLite 3.43+ compat
    decade_expr = (Movie.year - Movie.year % 10).label("decade")
    rows = (
        db.query(decade_expr, func.count())
        .filter(Movie.year.isnot(None))
        .group_by(literal_column("decade"))
        .order_by(literal_column("decade"))
        .all()
    )
    return {"labels": [f"{r[0]}s" for r in rows], "values": [r[1] for r in rows]}
