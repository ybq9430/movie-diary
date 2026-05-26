from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import OverviewResponse, ChartDataResponse
from services import stats_service

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse)
def overview(db: Session = Depends(get_db)):
    data = stats_service.get_overview(db)
    return OverviewResponse(**data)


@router.get("/rating-distribution", response_model=ChartDataResponse)
def rating_distribution(db: Session = Depends(get_db)):
    data = stats_service.get_rating_distribution(db)
    return ChartDataResponse(**data)


@router.get("/genre-preference", response_model=ChartDataResponse)
def genre_preference(db: Session = Depends(get_db)):
    data = stats_service.get_genre_preference(db)
    return ChartDataResponse(**data)


@router.get("/watching-trend", response_model=ChartDataResponse)
def watching_trend(db: Session = Depends(get_db)):
    data = stats_service.get_watching_trend(db)
    return ChartDataResponse(**data)


@router.get("/director-ranking", response_model=ChartDataResponse)
def director_ranking(db: Session = Depends(get_db)):
    data = stats_service.get_director_ranking(db)
    return ChartDataResponse(**data)


@router.get("/region-distribution", response_model=ChartDataResponse)
def region_distribution(db: Session = Depends(get_db)):
    data = stats_service.get_region_distribution(db)
    return ChartDataResponse(**data)


@router.get("/monthly-pattern", response_model=ChartDataResponse)
def monthly_pattern(db: Session = Depends(get_db)):
    data = stats_service.get_monthly_pattern(db)
    return ChartDataResponse(**data)


@router.get("/year-distribution", response_model=ChartDataResponse)
def year_distribution(db: Session = Depends(get_db)):
    data = stats_service.get_year_distribution(db)
    return ChartDataResponse(**data)
