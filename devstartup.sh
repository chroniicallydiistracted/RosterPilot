#!/usr/bin/env bash
set -euo pipefail

REPO="${HOME}/RosterPilot"
VENV="$REPO/.venv"

cd "$REPO"

# quick checks
python3 --version
node --version
npm --version

# create & activate a repo venv (avoids PEP 668)
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV" || {
    echo "ERROR: venv creation failed. Install python3-venv: sudo apt-get install -y python3-venv" >&2
    exit 1
  }
fi
# shellcheck source=/dev/null
source "$VENV/bin/activate"

# upgrade pip + tooling and install poetry into the venv
python -m pip install --upgrade pip setuptools wheel
python -m pip install "poetry==1.6.1"

# load repo env into the shell
if [ ! -f "$REPO/.env" ]; then
  echo "ERROR: $REPO/.env not found" >&2
  exit 1
fi
set -a
# shellcheck source=/dev/null
source "$REPO/.env"
set +a

# basic env sanity check
REQUIRED=(SESSION_SECRET TOKEN_ENC_KEY YAHOO_CLIENT_ID YAHOO_CLIENT_SECRET DATABASE_URL REDIS_URL NEXT_PUBLIC_API_URL NEXT_PUBLIC_WS_URL)
for k in "${REQUIRED[@]}"; do
  if [ -z "${!k:-}" ]; then
    echo "ERROR: required env var '$k' is not set in $REPO/.env" >&2
    exit 1
  fi
done

# Backend: install deps into the active venv, run migrations and tests
cd "$REPO/backend"
export POETRY_VIRTUALENVS_CREATE=false
poetry install --no-interaction --no-ansi
poetry run alembic upgrade head
poetry run pytest -q

# Frontend: install deps and start dev server
cd "$REPO/frontend"
npm ci
cp .env.production .env.local || true
npm run dev

# Optional root-level scripts (no-op if not needed)
cd "$REPO"
npm install || true

echo "Bootstrap complete."
