"""Application entry point for the RosterPilot backend service."""

from fastapi import FastAPI

from app.api.routes import health


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    app = FastAPI(
        title="RosterPilot API",
        version="0.1.0",
        description=(
            "Read-only Yahoo Fantasy companion with PyESPN game data and lineup optimization "
            "capabilities."
        ),
    )

    app.include_router(health.router)

    return app


app = create_app()
