"""Application entry point for the RosterPilot backend service."""

import os
from typing import Any

import sentry_sdk
from fastapi import APIRouter, FastAPI

from app.api.routes import games, health, leagues, me
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    # --- Observability Setup ---
    # Initialize Sentry for error tracking. This should be done as early as possible.
    if dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=dsn,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            profiles_sample_rate=1.0,
        )

    instrumentation_enabled = os.getenv("APP_ENV") == "production"
    fastapi_instrumentor: Any | None = None

    # Initialize OpenTelemetry for distributed tracing in production.
    # This uses the application's default credentials on Cloud Run.
    if instrumentation_enabled:
        from opentelemetry import trace
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        from opentelemetry.instrumentation.fastapi import (
            FastAPIInstrumentor,  # type: ignore[import]
        )
        from opentelemetry.instrumentation.httpx import (
            HTTPXClientInstrumentor,  # type: ignore[import]
        )
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        tracer_provider = TracerProvider()
        exporter = CloudTraceSpanExporter()
        processor = BatchSpanProcessor(exporter)
        tracer_provider.add_span_processor(processor)
        trace.set_tracer_provider(tracer_provider)

        # Instrument httpx to trace outgoing requests
        HTTPXClientInstrumentor().instrument()
        fastapi_instrumentor = FastAPIInstrumentor

    app = FastAPI(
        title="RosterPilot API",
        version="0.1.0",
        description=(
            "Read-only Yahoo Fantasy companion with PyESPN game data and lineup optimization "
            "capabilities."
        ),
    )

    # Instrument the FastAPI app after it's created for production
    if instrumentation_enabled and fastapi_instrumentor is not None:
        fastapi_instrumentor.instrument_app(app)

    settings = get_settings()

    app.include_router(health.router)

    api_router = APIRouter()
    api_router.include_router(me.router)
    api_router.include_router(leagues.router)
    api_router.include_router(games.router)

    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
