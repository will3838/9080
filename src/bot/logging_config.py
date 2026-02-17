"""Logging setup for the bot application."""

from __future__ import annotations

import logging
import sys


def setup_logging() -> None:
    """Configure root logging to stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
