"""Bot entrypoint."""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from openpyxl import Workbook
from telegram.ext import Application, CommandHandler

from bot.config import load_settings
from bot.errors.error_handler import on_error
from bot.handlers.help import help_command
from bot.logging_config import setup_logging


logger = logging.getLogger(__name__)


def ensure_item_excel_exists() -> None:
    data_dir = Path("data")
    item_dir = Path("item")
    file_path = data_dir / "item.xlsx"

    data_dir.mkdir(parents=True, exist_ok=True)
    item_dir.mkdir(parents=True, exist_ok=True)

    if file_path.exists():
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "item"
    ws["A1"] = "id"
    ws["B1"] = "name"
    ws["C1"] = "price"
    ws["D1"] = "chance"
    wb.save(file_path)


def main() -> None:
    """Configure and run the bot via long polling."""
    load_dotenv()
    setup_logging()
    ensure_item_excel_exists()

    settings = load_settings()

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(on_error)

    logger.info("Starting bot with long polling")
    application.run_polling()


if __name__ == "__main__":
    main()
