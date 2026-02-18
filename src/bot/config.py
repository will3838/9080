"""Application settings and validation."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Settings:
    telegram_bot_token: str


def load_settings() -> Settings:
    """Load and validate settings from environment variables."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing or empty. "
            "Set it via environment variable or .env file."
        )
    return Settings(telegram_bot_token=token)
