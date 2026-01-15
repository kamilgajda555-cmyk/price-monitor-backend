from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api import products, sources, alerts, reports, auth, dashboard, scraping, analytics
from app.models.database import engine, Base

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown

app = FastAPI(
    title=os.getenv("PROJECT_NAME", "Price Monitor"),
    openapi_url=f"{os.getenv('API_V1_STR', '/api/v1')}/openapi.json",
    lifespan=lifespan
)

# CORS - Fixed to handle comma-separated origins properly
cors_origins_str = os.getenv("BACKEND_CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

print(f"🔧 CORS Origins configured: {origins}")  # Debug log

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api_prefix = os.getenv("API_V1_STR", "/api/v1")
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["auth"])
app.include_router(dashboard.router, prefix=f"{api_prefix}/dashboard", tags=["dashboard"])
app.include_router(products.router, prefix=f"{api_prefix}/products", tags=["products"])
app.include_router(sources.router, prefix=f"{api_prefix}/sources", tags=["sources"])
app.include_router(alerts.router, prefix=f"{api_prefix}/alerts", tags=["alerts"])
app.include_router(reports.router, prefix=f"{api_prefix}/reports", tags=["reports"])
app.include_router(scraping.router, prefix=f"{api_prefix}/scrape", tags=["scraping"])
app.include_router(analytics.router, prefix=f"{api_prefix}/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Price Monitor API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
