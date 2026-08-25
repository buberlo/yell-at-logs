"""Entry point for running the package with ``python -m logguilt``.

This module is intentionally thin: all argument parsing and orchestration
live in :mod:`logguilt.cli`.  The only job here is to translate exceptions
into sensible process exit codes so that scripts and CI pipelines can rely
on a stable contract.

Usage::

    python -m logguilt tail app.log
    python -m logguilt import app.log --rules rules.json --poem haiku
"""

from __future__ import annotations

import sys

from logguilt.cli import main


def _run() -> int:
    """Invoke the CLI and map common exceptions to exit codes.

    Returns
    -------
    int
        Process exit code.  ``0`` on success, ``1`` on unexpected error,
        ``130`` when the user presses Ctrl-C.
    """
    try:
        return main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"logguilt: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_run())