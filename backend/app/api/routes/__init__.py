"""REST API routers available in the application."""

from app.api.routes import games, health, leagues, me, meta, oauth

__all__ = ["games", "health", "leagues", "me", "meta", "oauth"]
