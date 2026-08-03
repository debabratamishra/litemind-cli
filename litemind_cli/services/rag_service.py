"""
RAG service — document upload, status, file management and query streaming.

Mirrors litemind-ui's app/frontend/services/rag_service.py,
adapted for async httpx.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx

from ..config import config

logger = logging.getLogger(__name__)


class RAGService:
    """Async client for the /api/rag/* endpoints."""

    def __init__(self) -> None:
        self._base = config.fastapi_url
        self._timeout = httpx.Timeout(
            connect=float(config.connect_timeout),
            read=float(config.read_timeout),
            write=60.0,
            pool=5.0,
        )
        # Longer timeout for uploads / processing
        self._upload_timeout = httpx.Timeout(
            connect=float(config.connect_timeout),
            read=300.0,
            write=120.0,
            pool=5.0,
        )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    async def save_configuration(
        self,
        provider: str,
        embedding_model: str,
        embedding_backend: str | None = None,
        embedding_api_base: str | None = None,
        embedding_api_key: str | None = None,
        chunk_size: int = 500,
    ) -> tuple[bool, str]:
        """Save RAG configuration to the backend."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.post(
                    f"{self._base}/api/rag/save_config",
                    json={
                        "provider": provider,
                        "embedding_model": embedding_model,
                        "embedding_backend": embedding_backend,
                        "embedding_api_base": embedding_api_base,
                        "embedding_api_key": embedding_api_key,
                        "chunk_size": chunk_size,
                    },
                )
                if r.status_code == 200:
                    return True, "Configuration saved"
                return False, r.text
        except Exception as exc:
            return False, f"Configuration error: {exc}"

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    async def get_status(self) -> dict[str, Any] | None:
        """Return the current RAG system status."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.get(f"{self._base}/api/rag/status")
                if r.status_code == 200:
                    return r.json()
        except Exception as exc:
            logger.debug("RAG status error: %s", exc)
        return None

    async def reset_system(self) -> tuple[bool, str]:
        """Reset the entire RAG vector store."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.post(f"{self._base}/api/rag/reset")
                if r.status_code == 200:
                    return True, r.json().get("message", "RAG system reset successfully")
                return False, f"Reset failed ({r.status_code}): {r.text}"
        except Exception as exc:
            return False, f"Reset error: {exc}"

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    async def get_processed_files(self) -> dict[str, Any] | None:
        """Return information about all processed files."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.get(f"{self._base}/api/rag/files")
                if r.status_code == 200:
                    return r.json()
        except Exception as exc:
            logger.debug("RAG files error: %s", exc)
        return None

    async def remove_file(self, filename: str) -> tuple[bool, str]:
        """Remove a single file from the RAG index."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.delete(f"{self._base}/api/rag/files/{filename}")
                if r.status_code == 200:
                    return True, r.json().get("message", "File removed")
                return False, r.text
        except Exception as exc:
            return False, f"Remove error: {exc}"

    async def upload_files(
        self,
        file_paths: list[Path],
        chunk_size: int | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Upload one or more local files for ingestion.

        :param file_paths: Paths to local files to upload.
        :param chunk_size: Override default chunk size.
        :returns: (success, response_json)
        """
        if not file_paths:
            return False, {}
        chunk = chunk_size or config.default_chunk_size
        try:
            files = [
                ("files", (p.name, p.read_bytes(), _mime_for(p)))
                for p in file_paths
            ]
            async with httpx.AsyncClient(timeout=self._upload_timeout) as client:
                r = await client.post(
                    f"{self._base}/api/rag/upload",
                    files=files,
                    data={"chunk_size": str(chunk)},
                )
                if r.status_code == 200:
                    return True, r.json()
                logger.error("Upload failed %s: %s", r.status_code, r.text)
                return False, {}
        except Exception as exc:
            logger.error("Upload error: %s", exc)
            return False, {}

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    async def stream_rag_query(
        self,
        query: str,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        system_prompt: str = "",
        n_results: int | None = None,
        use_multi_agent: bool = False,
        use_hybrid_search: bool = False,
        backend: str | None = None,
        api_base: str | None = None,
        api_key: str | None = None,
        conversation_summary: str | None = None,
        session_id: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        frequency_penalty: float | None = None,
        repetition_penalty: float | None = None,
    ) -> AsyncIterator[str]:
        """Yield text chunks from a streaming RAG response."""
        payload: dict[str, Any] = {
            "query": query,
            "messages": messages,
            "model": model or config.default_model,
            "backend": backend or config.default_backend,
            "system_prompt": system_prompt,
            "n_results": n_results if n_results is not None else config.default_n_results,
            "use_multi_agent": use_multi_agent,
            "use_hybrid_search": use_hybrid_search,
            "temperature": temperature if temperature is not None else config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else config.max_tokens,
            "top_p": top_p if top_p is not None else config.top_p,
            "frequency_penalty": (
                frequency_penalty if frequency_penalty is not None else config.frequency_penalty
            ),
            "repetition_penalty": (
                repetition_penalty if repetition_penalty is not None else config.repetition_penalty
            ),
        }
        if api_base or config.api_base:
            payload["api_base"] = api_base or config.api_base
        if api_key or config.api_key:
            payload["api_key"] = api_key or config.api_key
        if conversation_summary:
            payload["conversation_summary"] = conversation_summary
        if session_id:
            payload["session_id"] = session_id

        headers = {}
        token = config.backend_token
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=self._timeout, headers=headers) as client:
            async with client.stream(
                "POST", f"{self._base}/api/rag/query", json=payload
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk:
                        yield chunk


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

_MIME_MAP = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".html": "text/html",
    ".htm": "text/html",
}


def _mime_for(path: Path) -> str:
    return _MIME_MAP.get(path.suffix.lower(), "application/octet-stream")


# Module-level singleton
rag_service = RAGService()
