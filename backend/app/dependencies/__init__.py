"""Dependency injection helpers for the FastAPI application."""

from app.dependencies.settings import provide_settings

__all__ = ["provide_settings"]
