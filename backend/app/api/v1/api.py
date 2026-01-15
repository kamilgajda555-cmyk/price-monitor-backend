from fastapi import APIRouter

from app.api import (
    auth,
    products,
    sources,
    alerts,
    dashboard,
    scraping,
    reports,
    analytics
)

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(scraping.router, prefix="/scrape", tags=["scraping"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
