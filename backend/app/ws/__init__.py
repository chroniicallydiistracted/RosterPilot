"""WebSocket routers and realtime helpers."""

from fastapi import APIRouter

from app.ws import games

router = APIRouter(prefix="/ws")
router.include_router(games.router)

__all__ = ["router"]
