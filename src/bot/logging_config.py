"""Logging configuration utilities."""

from __future__ import annotations

import logging
import sys


def setup_logging() -> None:
    """Configure application logging to stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
