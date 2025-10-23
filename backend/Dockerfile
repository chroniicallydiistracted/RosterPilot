# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Poetry and dependencies separately to leverage Docker layer caching
RUN pip install --upgrade pip && \
    pip install poetry==1.6.1

COPY pyproject.toml poetry.lock* /tmp/poetry/

WORKDIR /tmp/poetry
RUN poetry config virtualenvs.create false && \
    poetry install --only main

WORKDIR /app
COPY . /app

# Cloud Run provides PORT at runtime
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
