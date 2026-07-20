"""Smoke tests — verify the package imports and the CLI entrypoint works.

These do not require a running LiteMindUI backend (only --version / --help).
"""

from typer.testing import CliRunner

from litemind_cli import __version__
from litemind_cli.config import config
from litemind_cli.main import app

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "LiteMind" in result.stdout


def test_config_defaults() -> None:
    assert config.fastapi_url.startswith("http")
    assert config.default_model
    assert config.read_timeout > 0
