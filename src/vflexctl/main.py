import logging
import sys
from importlib.metadata import version

import structlog
import typer

from .cli import cli
from .context import AppContext

APP_NAME = "vflexctl"
__version__ = version(APP_NAME)
__version_str__ = f"{APP_NAME} {__version__}"


def configure_logging(verbose: bool, debug: bool) -> None:
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(level))


def show_version(val: bool) -> None:
    if not val:
        return
    typer.echo(__version_str__)
    sys.exit(0)


@cli.callback(help=__version_str__)
def main(
    ctx: typer.Context,
    deep_adjust: bool = typer.Option(
        False,
        "--deep-adjust",
        help='Use full handshake when setting values. Useful if the VFlex becomes "gone" while adjusting',
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    debug: bool = typer.Option(False, "--debug", "-vv", help="Enable debug logging"),
    _version: bool = typer.Option(
        False,
        "--version",
        help="Show version",
        is_eager=True,
        callback=show_version,
    ),
) -> None:
    """
    Global options for vflexctl.
    """
    configure_logging(verbose, debug)
    ctx.obj = AppContext(deep_adjust=deep_adjust)


if __name__ == "__main__":
    cli()
