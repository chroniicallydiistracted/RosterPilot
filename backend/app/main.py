"""Application entry point for the RosterPilot backend service."""

import os

from fastapi import FastAPI

# Sentry & OpenTelemetry
import sentry_sdk
from opentelemetry import trace
from opentelemetry.exporter.google_cloud_trace import GoogleCloudTraceSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.api.routes import health


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
            integrations=[sentry_sdk.integrations.fastapi.FastAPIIntegration()],
        )

    # Initialize OpenTelemetry for distributed tracing in production.
    # This uses the application's default credentials on Cloud Run.
    if os.getenv("APP_ENV") == "production":
        tracer_provider = TracerProvider()
        exporter = GoogleCloudTraceSpanExporter()
        processor = BatchSpanProcessor(exporter)
        tracer_provider.add_span_processor(processor)
        trace.set_tracer_provider(tracer_provider)

        # Instrument httpx to trace outgoing requests
        HTTPXClientInstrumentor().instrument()

    app = FastAPI(
        title="RosterPilot API",
        version="0.1.0",
        description=(
            "Read-only Yahoo Fantasy companion with PyESPN game data and lineup optimization "
            "capabilities."
        ),
    )

    # Instrument the FastAPI app after it's created for production
    if os.getenv("APP_ENV") == "production":
        FastAPIInstrumentor.instrument_app(app)

    app.include_router(health.router)

    return app


app = create_app()