"""Handler for /spin command."""

from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from telegram import Update
from telegram.ext import ContextTypes


async def spin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    items = context.application.bot_data.get("items")
    if not items:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    weights = [item["chance"] for item in items]
    selected_item = random.choices(items, weights=weights, k=1)[0]

    timestamp = datetime.now(timezone.utc).isoformat()
    user = update.effective_user
    chat = update.effective_chat

    user_id = user.id if user is not None else 0
    username = user.username if user is not None and user.username is not None else ""
    chat_id = chat.id if chat is not None else 0

    spin_file = Path("data") / "spin.xlsx"

    try:
        if not spin_file.exists():
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
            wb.save(spin_file)

        wb = load_workbook(spin_file)
        ws = wb["spin"] if "spin" in wb.sheetnames else wb.active
        ws.append(
            [
                timestamp,
                user_id,
                username,
                chat_id,
                selected_item["id"],
                selected_item["name"],
                selected_item["price"],
                selected_item["chance"],
            ]
        )
        wb.save(spin_file)
    except Exception:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    await update.message.reply_text(f"вам выпало {selected_item['name']}")
