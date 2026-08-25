"""guilt_poet: parse logs, score their guilt, and apologize in verse."""

__version__ = "0.1.0"
__all__ = ["__version__", "main"]


def main() -> int | None:
    """Run the guilt_poet command line interface.

    This entry point is intentionally lazy so that importing the package
    does not immediately load the CLI and its dependencies.

    Returns:
        The exit code returned by the CLI, if any.
    """
    from .cli import main as cli_main

    return cli_main()