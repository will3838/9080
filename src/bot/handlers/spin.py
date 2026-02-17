"""Handler for /spin command."""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _append_spin_log(
    user_id: int,
    username: str,
    chat_id: int,
    item_id: int,
    item_name: str,
    price: int,
    chance: float,
) -> None:
    file_path = Path("data") / "spin.xlsx"

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
        ws = wb.active

    ws.append(
        [
            datetime.now(timezone.utc).isoformat(),
            user_id,
            username,
            chat_id,
            item_id,
            item_name,
            price,
            chance,
        ]
    )
    wb.save(file_path)
    wb.close()


async def spin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pick item by chance and log spin result."""
    if update.message is None:
        return

    items = context.application.bot_data.get("items")
    if not isinstance(items, list) or not items:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    weights = [item["chance"] for item in items]
    item = random.choices(items, weights=weights, k=1)[0]

    user_id = update.effective_user.id if update.effective_user is not None else 0
    username = update.effective_user.username if update.effective_user and update.effective_user.username else ""
    chat_id = update.effective_chat.id if update.effective_chat is not None else 0

    try:
        _append_spin_log(
            user_id=user_id,
            username=username,
            chat_id=chat_id,
            item_id=item["id"],
            item_name=item["name"],
            price=item["price"],
            chance=item["chance"],
        )
    except Exception:
        logger.exception("Failed to write spin log")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return

    await update.message.reply_text(f"вам выпало {item['name']}")
