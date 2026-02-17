"""Application settings loading and validation."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings for the bot."""

    telegram_bot_token: str


def load_settings() -> Settings:
    """Load settings from environment and validate required values."""
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        raise RuntimeError(
            "Environment variable TELEGRAM_BOT_TOKEN is required and must not be empty."
        )

    return Settings(telegram_bot_token=token)
