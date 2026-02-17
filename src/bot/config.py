"""Configuration loading for the Telegram bot."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str


def load_settings() -> Settings:
    """Load and validate required application settings from environment."""
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set or empty. Set it in environment or .env file."
        )

    return Settings(telegram_bot_token=token)
