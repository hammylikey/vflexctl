import logging

import structlog
import typer

from .context import AppContext
from .cli import cli


def configure_logging(verbose: bool, debug: bool) -> None:
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(level))


@cli.callback()
def main(
    ctx: typer.Context,
    deep_adjust: bool = typer.Option(
        False,
        "--deep-adjust",
        help="Use long output format",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
) -> None:
    """
    Global options for vflexctl.
    """
    configure_logging(verbose, debug)
    ctx.obj = AppContext(deep_adjust=deep_adjust)


if __name__ == "__main__":
    cli()
