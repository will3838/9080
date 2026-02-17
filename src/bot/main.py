"""Bot entrypoint."""

from __future__ import annotations

import logging
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from openpyxl import Workbook, load_workbook
from telegram.ext import Application, CommandHandler

from bot.config import load_settings
from bot.errors.error_handler import on_error
from bot.handlers.help import help_command
from bot.handlers.spin import spin_command
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


def ensure_spin_excel_exists() -> None:
    data_dir = Path("data")
    file_path = data_dir / "spin.xlsx"

    data_dir.mkdir(parents=True, exist_ok=True)

    if file_path.exists():
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "spin"
    ws["A1"] = "timestamp"
    ws["B1"] = "user_id"
    ws["C1"] = "username"
    ws["D1"] = "chat_id"
    ws["E1"] = "item_id"
    ws["F1"] = "item_name"
    ws["G1"] = "price"
    ws["H1"] = "chance"
    wb.save(file_path)


def load_items_once() -> list[dict[str, object]]:
    file_path = Path("data/item.xlsx")
    if not file_path.exists():
        raise RuntimeError("data/item.xlsx does not exist")

    wb = load_workbook(file_path, data_only=True, read_only=True)
    try:
        if "item" not in wb.sheetnames:
            raise RuntimeError('Worksheet "item" does not exist in data/item.xlsx')

        ws = wb["item"]
        header = list(next(ws.iter_rows(min_row=1, max_row=1, values_only=True)))
        if header != ["id", "name", "price", "chance"]:
            raise RuntimeError("Invalid headers in data/item.xlsx. Expected: id, name, price, chance")

        items: list[dict[str, object]] = []
        for row_number, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            item_id, name, price, chance = row

            if not isinstance(item_id, int) or isinstance(item_id, bool):
                raise RuntimeError(f"Invalid id at row {row_number}")
            if not isinstance(name, str) or not name.strip():
                raise RuntimeError(f"Invalid name at row {row_number}")
            if not isinstance(price, int) or isinstance(price, bool):
                raise RuntimeError(f"Invalid price at row {row_number}")
            if not isinstance(chance, (float, Decimal)) or not (0 < chance < 1):
                raise RuntimeError(f"Invalid chance at row {row_number}")

            items.append(
                {
                    "id": item_id,
                    "name": name,
                    "price": price,
                    "chance": float(chance),
                }
            )

        if not items:
            raise RuntimeError("data/item.xlsx must contain at least one data row")

        return items
    finally:
        wb.close()


def main() -> None:
    """Configure and run the bot via long polling."""
    load_dotenv()
    setup_logging()
    ensure_item_excel_exists()
    ensure_spin_excel_exists()
    items = load_items_once()
    settings = load_settings()

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.bot_data["items"] = items
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("spin", spin_command))
    application.add_error_handler(on_error)

    logger.info("Starting bot with long polling")
    application.run_polling()


if __name__ == "__main__":
    main()
