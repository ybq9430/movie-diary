from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Identifiers
    douban_id = Column(String, unique=True, nullable=True)
    tmdb_id = Column(Integer, unique=True, nullable=True)
    # Core info
    title = Column(String, nullable=False)
    original_title = Column(String, nullable=True)
    english_title = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    # TMDB metadata
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    overview = Column(Text, nullable=True)
    tmdb_rating = Column(Float, nullable=True)
    runtime = Column(Integer, nullable=True)
    release_date = Column(String, nullable=True)
    # User data
    user_rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    impressions = Column(Text, nullable=True)
    watch_date = Column(String, nullable=True)
    is_favorite = Column(Boolean, default=False)
    # Normalized fields (JSON arrays as text)
    genres = Column(Text, nullable=True)
    directors = Column(Text, nullable=True)
    cast_ = Column("cast", Text, nullable=True)
    regions = Column(Text, nullable=True)
    languages = Column(Text, nullable=True)
    duration = Column(String, nullable=True)
    # Metadata
    source = Column(String, default="douban")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MovieTag(Base):
    __tablename__ = "movie_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    tag = Column(String, nullable=False)


class AIPersonality(Base):
    __tablename__ = "ai_personality"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis = Column(Text, nullable=False)
    movie_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AIPortrait(Base):
    __tablename__ = "ai_portrait"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(Text, nullable=True)
    image_path = Column(String, nullable=False)
    style = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_title = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    tmdb_id = Column(Integer, nullable=True)
    poster_path = Column(String, nullable=True)
    category = Column(String, nullable=True)
    is_watched = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
