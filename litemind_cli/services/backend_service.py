"""
Backend health / model listing service.

Mirrors the functionality of litemind-ui's
app/frontend/services/backend_service.py, but uses httpx instead of
requests so it works well inside async Textual workers.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ..config import config

logger = logging.getLogger(__name__)


class BackendService:
    """Thin client for the LiteMindUI FastAPI backend meta-endpoints."""

    def __init__(self) -> None:
        self._base = config.fastapi_url
        self._timeout = httpx.Timeout(
            connect=float(config.connect_timeout),
            read=float(config.read_timeout),
            write=30.0,
            pool=5.0,
        )

    # ------------------------------------------------------------------
    # Connectivity
    # ------------------------------------------------------------------

    async def check_health(self) -> bool:
        """Return True if the backend is reachable and healthy."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.get(f"{self._base}/health")
                return r.status_code == 200
        except Exception as exc:
            logger.debug("Health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Model listing
    # ------------------------------------------------------------------

    async def get_available_models(self) -> list[str]:
        """Return a flat list of model names from the backend."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.get(f"{self._base}/models")
                r.raise_for_status()
                return r.json().get("models", []) or ["default"]
        except Exception as exc:
            logger.warning("Could not fetch models: %s", exc)
            return ["default"]

    async def get_enhanced_models(self) -> dict[str, Any]:
        """Return local + cloud model listing with metadata."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.get(f"{self._base}/models/enhanced")
                r.raise_for_status()
                return r.json()
        except Exception as exc:
            logger.warning("Could not fetch enhanced models: %s", exc)
            return {"local_models": [], "cloud_models": []}

    # ------------------------------------------------------------------
    # Processing capabilities
    # ------------------------------------------------------------------

    async def get_processing_capabilities(self) -> dict[str, Any] | None:
        """Return available processing capabilities from the backend."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.get(f"{self._base}/api/processing/capabilities")
                if r.status_code == 200:
                    return r.json()
        except Exception as exc:
            logger.debug("Could not fetch capabilities: %s", exc)
        return None


# Module-level singleton
backend_service = BackendService()
