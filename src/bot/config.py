"""Application settings and environment validation."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str


def load_settings() -> Settings:
    """Load and validate required settings from environment variables."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Missing required environment variable TELEGRAM_BOT_TOKEN. "
            "Set it directly or provide it via .env file in project root."
        )
    return Settings(telegram_bot_token=token)
