from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api.v1.api import api_router
from app.models.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Price Monitor API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Always allow Netlify frontend
cors_origins_str = os.getenv("BACKEND_CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()] if cors_origins_str else [
    "https://quiet-gecko-10db7b.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173"
]
print(f"🔧 CORS Origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
