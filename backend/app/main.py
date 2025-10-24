"""Application entry point for the RosterPilot backend service."""

import os
import time
from typing import Any

import sentry_sdk
from fastapi import APIRouter, FastAPI, Request

from app.api.routes import games, health, leagues, me, meta, oauth
from app.core.config import get_settings
from app.core.metrics import RequestMetrics
from app.core.rate_limiter import SlidingWindowRateLimiter
from app.ws import router as ws_router


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
        try:
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
        except Exception:  # pragma: no cover - diagnostics for missing credentials
            instrumentation_enabled = False
            fastapi_instrumentor = None

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

    # ------------------------------------------------------------------
    # Runtime metrics & rate limiting primitives
    # ------------------------------------------------------------------
    app.state.request_metrics = RequestMetrics(max_samples=1024)
    app.state.rate_limiter = SlidingWindowRateLimiter(
        max_requests=settings.rate_limit_max,
        window_seconds=settings.rate_limit_window,
    )

    @app.middleware("http")
    async def record_request_metrics(request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        metrics: RequestMetrics | None = getattr(request.app.state, "request_metrics", None)
        if metrics is not None:
            metrics.record(request.url.path, duration_ms)
        response.headers.setdefault("X-Request-Duration-Ms", f"{duration_ms:.2f}")
        return response

    app.include_router(health.router)

    api_router = APIRouter()
    api_router.include_router(oauth.router)
    api_router.include_router(me.router)
    api_router.include_router(leagues.router)
    api_router.include_router(games.router)
    api_router.include_router(meta.router)

    app.include_router(api_router, prefix=settings.api_prefix)
    app.include_router(ws_router)

    return app


app = create_app()
