"""Global application error handler."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log traceback and notify user with a short message when possible."""
    logger.exception("Unhandled exception while processing update", exc_info=context.error)

    if not isinstance(update, Update) or update.effective_message is None:
        return

    try:
        await update.effective_message.reply_text("Произошла ошибка. Попробуйте позже.")
    except Exception:
        logger.exception("Failed to send error message to user")
