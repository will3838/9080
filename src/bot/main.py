"""Bot entrypoint."""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation
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
    if not item_dir.exists():
        raise RuntimeError("item folder is missing: ./item")

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


def load_items_once() -> list[dict[str, int | str | float]]:
    item_file = Path("data") / "item.xlsx"

    if not item_file.exists():
        raise RuntimeError("data/item.xlsx does not exist")

    wb = load_workbook(item_file, data_only=True)

    if "item" not in wb.sheetnames:
        raise RuntimeError("Worksheet 'item' does not exist in data/item.xlsx")

    ws = wb["item"]
    header = [ws["A1"].value, ws["B1"].value, ws["C1"].value, ws["D1"].value]
    if header != ["id", "name", "price", "chance"]:
        raise RuntimeError("Invalid header in data/item.xlsx")

    items: list[dict[str, int | str | float]] = []

    for row_index, row in enumerate(ws.iter_rows(min_row=2, max_col=4, values_only=True), start=2):
        row_id, row_name, row_price, row_chance = row

        if not isinstance(row_id, int) or isinstance(row_id, bool):
            raise RuntimeError(f"Invalid id at row {row_index}")

        if not isinstance(row_name, str) or not row_name.strip():
            raise RuntimeError(f"Invalid name at row {row_index}")

        if not isinstance(row_price, int) or isinstance(row_price, bool):
            raise RuntimeError(f"Invalid price at row {row_index}")

        if isinstance(row_chance, bool):
            raise RuntimeError(f"Invalid chance at row {row_index}")

        try:
            chance_decimal = Decimal(str(row_chance))
        except (InvalidOperation, TypeError):
            raise RuntimeError(f"Invalid chance at row {row_index}") from None

        if not (Decimal("0") < chance_decimal < Decimal("1")):
            raise RuntimeError(f"Invalid chance at row {row_index}")

        items.append(
            {
                "id": row_id,
                "name": row_name,
                "price": row_price,
                "chance": float(chance_decimal),
            }
        )

    if not items:
        raise RuntimeError("data/item.xlsx must contain at least one data row")

    return items


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
