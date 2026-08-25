"""Entry point for running the CLI with ``python -m guilt_poet``."""

from __future__ import annotations

import sys

from .cli import main


def _run() -> int:
    """Run the CLI and normalize common interruption handling."""
    try:
        return main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(_run())