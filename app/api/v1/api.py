from fastapi import APIRouter

from app.api.v1.endpoints import spellcheck, predict, chat, files, coherence

api_router = APIRouter()

api_router.include_router(spellcheck.router, tags=["Spell Check"])
api_router.include_router(predict.router, tags=["Predictions"])
api_router.include_router(chat.router, tags=["Chat"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(coherence.router, tags=["Coherence"])
