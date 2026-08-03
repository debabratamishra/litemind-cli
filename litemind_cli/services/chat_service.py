"""
Chat service — streaming and non-streaming chat calls.

/api/chat/stream  sends SSE:  data: {"chunk": "..."}\n\n
/api/chat/web-search sends plain text chunks

Both are normalised here so callers always receive plain text strings.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from ..config import config

logger = logging.getLogger(__name__)


def _parse_sse_chunk(raw: str) -> str:
    """
    Extract text from a single SSE line or plain-text chunk.

    The /api/chat/stream endpoint emits:
        data: {"chunk": "hello"}\n\n

    We strip the 'data: ' prefix and decode the JSON.
    If the line is plain text (web-search endpoint) it is returned as-is.
    """
    text = raw.strip()
    if not text:
        return ""
    # Handle SSE envelope
    if text.startswith("data:"):
        text = text[len("data:"):].strip()
    if not text:
        return ""
    # Try to decode JSON {"chunk": "..."}
    try:
        obj = json.loads(text)
        # {"chunk": "..."} is the chat stream format
        if isinstance(obj, dict):
            return obj.get("chunk", obj.get("text", obj.get("content", "")))
    except (json.JSONDecodeError, ValueError):
        pass
    # Plain text — return as-is
    return text


class ChatService:
    """Async client for the /api/chat* endpoints."""

    def __init__(self) -> None:
        self._base = config.fastapi_url
        self._timeout = httpx.Timeout(
            connect=float(config.connect_timeout),
            read=float(config.read_timeout),
            write=30.0,
            pool=5.0,
        )

    # ------------------------------------------------------------------
    # Streaming chat  (SSE → plain text)
    # ------------------------------------------------------------------

    async def stream_chat(
        self,
        message: str,
        *,
        model: str | None = None,
        backend: str | None = None,
        api_base: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        frequency_penalty: float | None = None,
        repetition_penalty: float | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        conversation_summary: str | None = None,
        session_id: str | None = None,
    ) -> AsyncIterator[str]:
        """Yield plain-text chunks from the streaming chat endpoint."""
        payload = self._build_payload(
            message=message,
            model=model, backend=backend, api_base=api_base, api_key=api_key,
            temperature=temperature, max_tokens=max_tokens, top_p=top_p,
            frequency_penalty=frequency_penalty, repetition_penalty=repetition_penalty,
            conversation_history=conversation_history,
            conversation_summary=conversation_summary,
            session_id=session_id,
        )

        headers = self._auth_headers()

        async with httpx.AsyncClient(timeout=self._timeout, headers=headers) as client:
            async with client.stream("POST", f"{self._base}/api/chat/stream", json=payload) as resp:
                resp.raise_for_status()
                # The backend sends SSE lines: "data: {...}\n\n"
                # aiter_lines gives us one logical line at a time.
                async for line in resp.aiter_lines():
                    text = _parse_sse_chunk(line)
                    if text:
                        yield text

    # ------------------------------------------------------------------
    # Web-search chat  (plain text)
    # ------------------------------------------------------------------

    async def stream_web_search_chat(
        self,
        message: str,
        *,
        model: str | None = None,
        backend: str | None = None,
        api_base: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        conversation_summary: str | None = None,
        session_id: str | None = None,
    ) -> AsyncIterator[str]:
        """Yield plain-text chunks from the web-search chat endpoint."""
        payload: dict[str, Any] = {
            "message": message,
            "model": model or config.default_model,
            "backend": backend or config.default_backend,
            "temperature": temperature if temperature is not None else config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else config.max_tokens,
            "use_web_search": True,
        }
        if api_base or config.api_base:
            payload["api_base"] = api_base or config.api_base
        if api_key or config.api_key:
            payload["api_key"] = api_key or config.api_key
        if conversation_history:
            payload["conversation_history"] = conversation_history
        if conversation_summary:
            payload["conversation_summary"] = conversation_summary
        if session_id:
            payload["session_id"] = session_id

        headers = self._auth_headers()

        async with httpx.AsyncClient(timeout=self._timeout, headers=headers) as client:
            async with client.stream("POST", f"{self._base}/api/chat/web-search", json=payload) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_text():
                    if chunk:
                        yield chunk

    # ------------------------------------------------------------------
    # Memory management
    # ------------------------------------------------------------------

    async def get_memory_stats(self, session_id: str) -> dict[str, Any] | None:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.get(f"{self._base}/api/chat/memory/stats/{session_id}")
                if r.status_code == 200:
                    return r.json()
        except Exception as exc:
            logger.debug("Memory stats error: %s", exc)
        return None

    async def clear_memory(self, session_id: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.post(f"{self._base}/api/chat/memory/clear/{session_id}")
                return r.status_code == 200
        except Exception as exc:
            logger.debug("Clear memory error: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        """Return an Authorization header dict when a backend token is available."""
        token = config.backend_token
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def _build_payload(
        self,
        *,
        message: str,
        model: str | None,
        backend: str | None,
        api_base: str | None,
        api_key: str | None,
        temperature: float | None,
        max_tokens: int | None,
        top_p: float | None,
        frequency_penalty: float | None,
        repetition_penalty: float | None,
        conversation_history: list[dict[str, str]] | None,
        conversation_summary: str | None,
        session_id: str | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "message": message,
            "model": model or config.default_model,
            "backend": backend or config.default_backend,
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
        if conversation_history:
            payload["conversation_history"] = conversation_history
        if conversation_summary:
            payload["conversation_summary"] = conversation_summary
        if session_id:
            payload["session_id"] = session_id
        return payload


# Module-level singleton
chat_service = ChatService()
