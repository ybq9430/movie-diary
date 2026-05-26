import json
import csv
import logging
import re
import traceback
from pathlib import Path

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import Movie
from schemas import ImportStatusResponse

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter()

# Global state for import progress
_import_status = {"status": "idle", "movie_count": 0, "message": ""}
_enrich_status = {"status": "idle", "movie_count": 0, "message": ""}


def _clean_directors(raw: str) -> list[str]:
    """Clean polluted director field from CSV."""
    if not raw:
        return []
    # Scraper outputs " / " separated strings; try that first
    if " / " in raw:
        items = [x.strip() for x in raw.split(" / ")]
    else:
        try:
            items = json.loads(raw.replace("'", '"'))
        except (json.JSONDecodeError, ValueError):
            items = [x.strip() for x in raw.strip("[]").replace("'", "").split(",")]

    known_regions = {
        "中国大陆", "中国香港", "中国台湾", "美国", "日本", "韩国", "英国", "法国",
        "德国", "意大利", "西班牙", "印度", "泰国", "澳大利亚", "加拿大", "俄罗斯",
    }
    known_languages = {"粤语", "汉语普通话", "英语", "日语", "韩语", "法语", "德语"}

    cleaned = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        if item in known_regions:
            continue
        if item in known_languages:
            continue
        if item.startswith("http"):
            continue
        if len(item) > 20:
            continue
        # Skip items that look like movie titles (contain / or are very long)
        if "/" in item and len(item) > 10:
            continue
        cleaned.append(item)

    return cleaned


def _clean_genres(raw: str) -> list[str]:
    """Clean polluted genre field from CSV."""
    if not raw:
        return []
    # Scraper outputs " / " separated strings; try that first
    if " / " in raw:
        items = [x.strip() for x in raw.split(" / ")]
    else:
        try:
            items = json.loads(raw.replace("'", '"'))
        except (json.JSONDecodeError, ValueError):
            items = [x.strip() for x in raw.strip("[]").replace("'", "").split(",")]

    known_genres = {
        "剧情", "喜剧", "动作", "爱情", "科幻", "动画", "悬疑", "惊悚", "恐怖",
        "犯罪", "冒险", "奇幻", "战争", "历史", "传记", "音乐", "歌舞", "家庭",
        "纪录片", "西部", "武侠", "古装", "短片", "真人秀", "舞台艺术", "戏曲",
    }
    known_languages = {"粤语", "汉语普通话", "英语", "日语", "韩语", "法语", "德语", "意大利语"}

    cleaned = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        if item in known_genres:
            cleaned.append(item)
        elif item in known_languages:
            continue
        elif len(item) <= 4 and not any(c.isascii() for c in item):
            # Short Chinese text might be a genre we missed
            cleaned.append(item)

    return cleaned


def _import_csv_background(csv_path: str):
    """Background task to import CSV into database."""
    global _import_status
    _import_status = {"status": "running", "movie_count": 0, "message": "正在导入..."}

    db = SessionLocal()
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Check if already imported
                douban_id = row.get("subject_id", "").strip()
                if douban_id:
                    existing = db.query(Movie).filter(Movie.douban_id == douban_id).first()
                    if existing:
                        continue

                # Clean data
                title = row.get("title", "").split("/")[0].strip()
                if not title:
                    continue

                year_str = row.get("year", "").strip()
                year = int(year_str) if year_str.isdigit() else None

                directors = _clean_directors(row.get("director", ""))
                genres = _clean_genres(row.get("genre", ""))

                region_raw = row.get("region", "").strip()
                regions = [region_raw] if region_raw else []

                # Languages
                language_raw = row.get("language", "").strip()
                languages = [l.strip() for l in language_raw.split(" / ") if l.strip()] if " / " in language_raw else ([language_raw] if language_raw else [])

                duration = row.get("duration", "").strip() or None

                # User rating (1-5 stars)
                rating_str = row.get("user_rating", "").strip()
                user_rating = int(rating_str) if rating_str.isdigit() and 1 <= int(rating_str) <= 5 else None

                # Poster URL (from detail page scraping)
                poster_url = row.get("poster_url", "").strip() or None

                # Cast
                cast_raw = row.get("cast", "").strip()
                cast_list = [c.strip() for c in cast_raw.split(" / ") if c.strip()] if " / " in cast_raw else ([cast_raw] if cast_raw else [])

                movie = Movie(
                    douban_id=douban_id,
                    title=title,
                    year=year,
                    watch_date=row.get("watch_date", "").strip() or None,
                    comment=row.get("comment", "").strip() or None,
                    user_rating=user_rating,
                    poster_path=poster_url,
                    genres=json.dumps(genres, ensure_ascii=False),
                    directors=json.dumps(directors, ensure_ascii=False),
                    cast_=json.dumps(cast_list, ensure_ascii=False),
                    regions=json.dumps(regions, ensure_ascii=False),
                    languages=json.dumps(languages, ensure_ascii=False),
                    duration=duration,
                    source="douban",
                )
                db.add(movie)
                count += 1

                if count % 50 == 0:
                    db.commit()
                    _import_status["movie_count"] = count
                    _import_status["message"] = f"已导入 {count} 部..."

            db.commit()
            _import_status = {"status": "completed", "movie_count": count, "message": f"导入完成，共 {count} 部电影"}

    except Exception as e:
        logger.error(f"CSV 导入失败: {e}\n{traceback.format_exc()}")
        _import_status = {"status": "failed", "movie_count": 0, "message": str(e)}
    finally:
        db.close()


@router.post("/csv")
def import_csv(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Import from the existing CSV file."""
    from config import CSV_PATH
    if not CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    background_tasks.add_task(_import_csv_background, str(CSV_PATH))
    return {"message": "Import started", "status": "running"}


@router.post("/csv/upload")
async def import_csv_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Import from an uploaded CSV file."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="仅支持 CSV 文件")

    # Sanitize filename
    safe_name = re.sub(r"[^\w\-.]", "_", Path(file.filename).stem) + ".csv"

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    # Validate content is text/CSV (not binary)
    try:
        sample = content[:1024].decode("utf-8-sig")
        # CSV should contain at least one comma or newline
        if "," not in sample and "\n" not in sample:
            raise HTTPException(status_code=400, detail="文件内容不是有效的 CSV 格式")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="文件编码不是有效的 UTF-8")

    upload_dir = Path(__file__).parent.parent / "static" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / safe_name

    with open(file_path, "wb") as f:
        f.write(content)

    background_tasks.add_task(_import_csv_background, str(file_path))
    return {"message": "Import started", "status": "running"}


@router.get("/status", response_model=ImportStatusResponse)
def get_import_status():
    return ImportStatusResponse(**_import_status)


def _enrich_background(missing_ids: list[str]):
    """Background task to enrich movie data from Douban."""
    import time
    import requests
    from bs4 import BeautifulSoup
    from config import HEADERS_TEMPLATE, random_delay, DELAY_DETAIL_PAGE

    global _enrich_status
    _enrich_status = {"status": "running", "movie_count": 0, "message": "正在补充数据..."}
    total = len(missing_ids)
    enriched = 0

    db = SessionLocal()
    try:
        for i, douban_id in enumerate(missing_ids):
            try:
                time.sleep(random_delay(DELAY_DETAIL_PAGE))
                detail_url = f"https://movie.douban.com/subject/{douban_id}/"
                resp = requests.get(detail_url, headers=HEADERS_TEMPLATE, timeout=15)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                movie = db.query(Movie).filter(Movie.douban_id == douban_id).first()
                if not movie:
                    continue

                mainpic = soup.select_one("#mainpic img")
                if mainpic and mainpic.get("src") and not movie.poster_path:
                    movie.poster_path = mainpic["src"]

                link_report = soup.select_one("#link-report span.all") or soup.select_one("#link-report span")
                if link_report and not movie.overview:
                    overview = link_report.get_text(strip=True)
                    if overview:
                        movie.overview = overview

                enriched += 1
                if enriched % 10 == 0:
                    db.commit()
                    _enrich_status["movie_count"] = enriched
                    _enrich_status["message"] = f"已补充 {enriched}/{total} 部..."
            except Exception:
                continue

        db.commit()
        _enrich_status = {"status": "completed", "movie_count": enriched, "message": f"补充完成，共 {enriched}/{total} 部电影"}
    except Exception as e:
        logger.error(f"数据补充失败: {e}\n{traceback.format_exc()}")
        _enrich_status = {"status": "failed", "movie_count": 0, "message": str(e)}
    finally:
        db.close()


@router.post("/enrich")
def enrich_all(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """补充缺少海报和简介的电影数据（从豆瓣重新抓取）"""
    if _enrich_status["status"] == "running":
        return {"message": "补充任务正在运行中", "status": "running"}
    movies = db.query(Movie).filter(
        (Movie.poster_path.is_(None)) | (Movie.overview.is_(None))
    ).all()
    missing_ids = [m.douban_id for m in movies if m.douban_id]
    if not missing_ids:
        return {"message": "没有需要补充的电影", "enriched": 0, "total": 0}
    background_tasks.add_task(_enrich_background, missing_ids)
    return {"message": f"开始补充 {len(missing_ids)} 部电影", "status": "running"}


@router.get("/enrich/status", response_model=ImportStatusResponse)
def get_enrich_status():
    return ImportStatusResponse(**_enrich_status)
