"""Global error handler for the Telegram bot."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes


LOGGER = logging.getLogger(__name__)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log exception traceback and try to notify the user."""
    LOGGER.exception("Unhandled exception while processing update", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message is not None:
        try:
            await update.effective_message.reply_text("Произошла ошибка. Попробуйте позже.")
        except Exception:
            LOGGER.exception("Failed to send error message to user")
