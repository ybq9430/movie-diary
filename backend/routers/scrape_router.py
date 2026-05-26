import csv
import logging
import sys
import traceback
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add project root to path so we can import the scraper
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scraper import scrape_all

logger = logging.getLogger(__name__)
router = APIRouter()

_scrape_status = {
    "status": "idle",       # idle | running | completed | failed
    "movie_count": 0,
    "total_pages": 0,
    "message": "",
    "user_id": "",
}
_scrape_results: list[dict] = []
_csv_path: str | None = None

EXPORT_DIR = Path(__file__).resolve().parent.parent / "static" / "exports"


class ScrapeRequest(BaseModel):
    user_id: str
    cookie: str = ""
    detail: bool = True


def _run_scrape(user_id: str, cookie: str, detail: bool):
    global _scrape_results, _csv_path
    _scrape_status.update({
        "status": "running",
        "movie_count": 0,
        "total_pages": 0,
        "message": f"开始抓取用户 {user_id} 的观影记录...",
        "user_id": user_id,
    })
    _scrape_results = []
    _csv_path = None

    try:
        movies = scrape_all(user_id, cookie, detail=detail)

        if not movies:
            _scrape_status.update({
                "status": "failed",
                "message": "未抓取到任何数据，请检查用户 ID 是否正确，或该用户是否设置了公开可见。",
            })
            return

        _scrape_results = movies
        _scrape_status.update({
            "movie_count": len(movies),
            "message": f"抓取完成，共 {len(movies)} 部电影",
        })

        # Save CSV
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        csv_file = EXPORT_DIR / f"douban_{user_id}.csv"
        if movies:
            keys = movies[0].keys()
            with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(movies)
            _csv_path = str(csv_file)

        _scrape_status["status"] = "completed"

    except Exception as e:
        logger.error(f"抓取失败: {e}\n{traceback.format_exc()}")
        _scrape_status.update({
            "status": "failed",
            "message": f"抓取出错: {str(e)}",
        })


@router.post("")
def start_scrape(req: ScrapeRequest, background_tasks: BackgroundTasks):
    if _scrape_status["status"] == "running":
        raise HTTPException(status_code=409, detail="已有抓取任务正在运行，请稍后再试")
    background_tasks.add_task(_run_scrape, req.user_id, req.cookie, req.detail)
    return {"message": "抓取已启动", "status": "running"}


@router.get("/status")
def get_scrape_status():
    return _scrape_status


@router.get("/results")
def get_scrape_results(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    if not _scrape_results:
        return {"items": [], "total": 0, "page": 1, "per_page": per_page, "pages": 0}

    total = len(_scrape_results)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    items = _scrape_results[start:start + per_page]
    return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}


@router.get("/download")
def download_csv():
    if not _csv_path or not Path(_csv_path).exists():
        raise HTTPException(status_code=404, detail="CSV 文件不存在，请先完成抓取")
    return FileResponse(
        path=_csv_path,
        filename=Path(_csv_path).name,
        media_type="text/csv",
    )
