import logging

from .cli import cli
import typer
import structlog


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
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
) -> None:
    """
    Global options for vflexctl.
    """
    configure_logging(verbose, debug)


if __name__ == "__main__":
    cli()
