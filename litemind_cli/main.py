"""
CLI entrypoint for litemind-cli

Usage
-----
  litemind-cli                 # open TUI on Chat tab
  litemind-cli chat            # same as above
  litemind-cli rag             # open TUI on RAG tab
  litemind-cli status          # check backend health and exit
"""

from __future__ import annotations

from typing import Annotated, Optional

import httpx
import typer

from . import __version__

app = typer.Typer(
    name="litemind-cli",
    help="LiteMind CLI — terminal interface for the LiteMindUI backend.",
    add_completion=False,
    no_args_is_help=False,
)


# ---------------------------------------------------------------------------
# Shared options
# ---------------------------------------------------------------------------

def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"litemind-cli {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    backend: Annotated[
        Optional[str],
        typer.Option("--backend", "-b", help="Backend URL (overrides FASTAPI_URL env var)"),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Model name (overrides DEFAULT_MODEL env var)"),
    ] = None,
    version: Annotated[
        bool,
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show version and exit"),
    ] = False,
) -> None:
    """Open the TUI (defaults to Chat screen)."""
    if ctx.invoked_subcommand is None:
        _run_tui(tab="chat", backend=backend, model=model)


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

@app.command()
def chat(
    backend: Annotated[
        Optional[str],
        typer.Option("--backend", "-b", help="Backend URL"),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Model name"),
    ] = None,
) -> None:
    """Open the TUI on the Chat screen."""
    _run_tui(tab="chat", backend=backend, model=model)


@app.command()
def rag(
    backend: Annotated[
        Optional[str],
        typer.Option("--backend", "-b", help="Backend URL"),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Model name"),
    ] = None,
) -> None:
    """Open the TUI on the RAG screen."""
    _run_tui(tab="rag", backend=backend, model=model)


@app.command()
def login(
    backend: Annotated[
        Optional[str],
        typer.Option("--backend", "-b", help="Backend URL"),
    ] = None,
) -> None:
    """Authenticate with the backend and save the session token."""
    import asyncio

    from .config import config

    if backend:
        config.fastapi_url = backend

    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True)

    async def _login() -> None:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            r = await client.post(
                f"{config.fastapi_url}/api/auth/login",
                json={"email": email, "password": password},
            )
        if r.status_code == 200:
            token = r.json().get("access_token")
            if token:
                config.backend_token = token
                typer.echo(typer.style("✓ Login successful", fg=typer.colors.GREEN))
            else:
                typer.echo(typer.style("✗ No token in response", fg=typer.colors.RED))
                raise typer.Exit(code=1)
        else:
            typer.echo(
                typer.style(
                    f"✗ Login failed ({r.status_code}): {r.text}",
                    fg=typer.colors.RED,
                )
            )
            raise typer.Exit(code=1)

    asyncio.run(_login())


@app.command()
def status(
    backend: Annotated[
        Optional[str],
        typer.Option("--backend", "-b", help="Backend URL"),
    ] = None,
) -> None:
    """Check backend connectivity and print status."""
    import asyncio

    from .config import config
    from .services.backend_service import backend_service

    if backend:
        config.fastapi_url = backend

    async def _check() -> None:
        ok = await backend_service.check_health()
        if ok:
            typer.echo(typer.style(f"✓ Backend reachable at {config.fastapi_url}", fg=typer.colors.GREEN))
            # Print available models
            models = await backend_service.get_available_models()
            typer.echo(f"  Models: {', '.join(models)}")
        else:
            typer.echo(
                typer.style(f"✗ Backend NOT reachable at {config.fastapi_url}", fg=typer.colors.RED)
            )
            raise typer.Exit(code=1)

    asyncio.run(_check())


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_tui(tab: str, backend: str | None, model: str | None) -> None:
    """Apply CLI overrides and launch the Textual app."""
    from .config import config

    if backend:
        config.fastapi_url = backend
    if model:
        config.default_model = model

    from .app import LiteMindApp

    LiteMindApp(initial_tab=tab, model=model or config.default_model).run()
