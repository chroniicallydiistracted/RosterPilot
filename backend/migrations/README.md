# Database Migrations

Alembic is configured for the RosterPilot backend. The initial revision `20251023_0001_initial_schema`
creates the scaffold schema captured in `INSTRUCTIONS.md`.

## Usage

```bash
cd backend
poetry run alembic upgrade head
```

Set `DATABASE_URL` in your environment or `.env` before running Alembic commands. The configuration
will fall back to the URL defined in `alembic.ini` if present.
