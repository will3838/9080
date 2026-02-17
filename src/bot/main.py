"""Application entrypoint for Telegram long-polling bot."""

from __future__ import annotations

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from bot.config import load_settings
from bot.errors.error_handler import on_error
from bot.handlers.help import help_command
from bot.logging_config import setup_logging


def main() -> None:
    """Run Telegram bot via long polling."""
    load_dotenv()
    setup_logging()
    settings = load_settings()

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(on_error)

    application.run_polling()


if __name__ == "__main__":
    main()
