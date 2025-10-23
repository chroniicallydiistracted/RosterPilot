"""PyESPN client scaffolding for official NFL data."""

from dataclasses import dataclass
from typing import Any

from app.core.config import Settings


@dataclass
class PyESPNClient:
    """Placeholder wrapper around PyESPN utilities."""

    settings: Settings

    async def get_schedule(self, season: int) -> Any:  # pragma: no cover - placeholder
        """Retrieve the NFL schedule for the provided season (stub)."""
        raise NotImplementedError("PyESPN integration not yet implemented.")
