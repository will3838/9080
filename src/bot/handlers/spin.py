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

    item_id = selected_item["id"]
    png_path = Path("item") / f"{item_id}.png"
    jpg_path = Path("item") / f"{item_id}.jpg"

    existing_images = [path for path in (png_path, jpg_path) if path.exists()]
    if len(existing_images) != 1:
        raise RuntimeError(f"Expected exactly one image for item id {item_id}")

    image_path = existing_images[0]
    if image_path.name not in {f"{item_id}.png", f"{item_id}.jpg"}:
        raise RuntimeError(f"Invalid image filename for item id {item_id}")

    spin_file = Path("data") / "spin.xlsx"

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

    with image_path.open("rb") as image_file:
        await update.message.reply_photo(
            photo=image_file,
            caption=f"вам выпало {selected_item['name']}",
        )
