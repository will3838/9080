"""Handler for /spin command."""

from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from telegram import Update
from telegram.ext import ContextTypes


def _append_spin_log(update: Update, item: dict[str, object]) -> None:
    file_path = Path("data/spin.xlsx")

    if not file_path.exists():
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
    else:
        wb = load_workbook(file_path)
        ws = wb["spin"] if "spin" in wb.sheetnames else wb.active

    try:
        user = update.effective_user
        chat = update.effective_chat
        ws.append(
            [
                datetime.now(timezone.utc).isoformat(),
                user.id if user is not None else 0,
                user.username if user is not None and user.username is not None else "",
                chat.id if chat is not None else 0,
                item["id"],
                item["name"],
                item["price"],
                item["chance"],
            ]
        )
        wb.save(file_path)
    finally:
        wb.close()


async def spin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pick a random item using weighted chance and log the result."""
    message = update.effective_message
    if message is None:
        return

    items = context.application.bot_data.get("items")
    if not isinstance(items, list) or not items:
        await message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    selected_item = random.choices(items, weights=[item["chance"] for item in items], k=1)[0]

    try:
        _append_spin_log(update, selected_item)
    except Exception:
        await message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    await message.reply_text(f"вам выпало {selected_item['name']}")
