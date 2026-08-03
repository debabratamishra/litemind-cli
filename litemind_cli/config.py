"""
Configuration for litemind-cli.

Values are loaded from environment variables / .env file.
They can be overridden at runtime by the CLI flags (see main.py).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load .env from the project root (sibling or parent of cwd).
load_dotenv()


@dataclass
class Config:
    """All runtime configuration for the CLI."""

    # Backend connection
    fastapi_url: str = field(
        default_factory=lambda: os.getenv("FASTAPI_URL", "http://localhost:8000")
    )
    connect_timeout: int = field(
        default_factory=lambda: int(os.getenv("CONNECT_TIMEOUT", "5"))
    )
    read_timeout: int = field(
        default_factory=lambda: int(os.getenv("READ_TIMEOUT", "600"))
    )

    # LLM defaults
    default_backend: str = field(
        default_factory=lambda: os.getenv("DEFAULT_BACKEND", "ollama")
    )
    default_model: str = field(
        default_factory=lambda: os.getenv("DEFAULT_MODEL", "llama3.2")
    )
    api_base: str | None = field(
        default_factory=lambda: os.getenv("API_BASE")
    )
    api_key: str | None = field(
        default_factory=lambda: os.getenv("API_KEY")
    )
    backend_token: str | None = field(
        default_factory=lambda: os.getenv("BACKEND_TOKEN")
    )

    # Generation defaults — match the litemind-ui frontend defaults
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    repetition_penalty: float = 1.0

    # RAG defaults
    default_chunk_size: int = 500
    default_n_results: int = 3

    # Logging
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )


# Module-level singleton — screens and services import this directly.
config = Config()
