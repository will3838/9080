"""Handler for /help command."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply with the required one-line help text."""
    del context
    if update.message is None:
        return
    await update.message.reply_text("автор @HATE_death_ME")
