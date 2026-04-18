from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.nlp_service import nlp_service
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load SymSpell dictionary
    nlp_service.load()
    yield


app = FastAPI(
    title="TextifyAI API",
    description="AI-powered writing assistant backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
raw_frontend_url = settings.FRONTEND_URL
allowed_origins = [origin.strip().rstrip("/") for origin in raw_frontend_url.split(",")]
# Add some standard variations for robustness
final_origins = []
for origin in allowed_origins:
    final_origins.append(origin)
    final_origins.append(f"{origin}/")

# Always allow localhost for development
if "http://localhost:5173" not in final_origins:
    final_origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=final_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "service": "TextifyAI API"}
