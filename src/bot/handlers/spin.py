"""Handler for /spin command."""

from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook
from telegram import Update
from telegram.ext import ContextTypes


def _resolve_item_image_path(item_id: int) -> Path:
    png_path = Path("item") / f"{item_id}.png"
    jpg_path = Path("item") / f"{item_id}.jpg"

    png_exists = png_path.exists()
    jpg_exists = jpg_path.exists()

    if png_exists and jpg_exists:
        raise RuntimeError(f"Multiple image files found for item id {item_id}")

    if not png_exists and not jpg_exists:
        raise RuntimeError(f"Image file is missing for item id {item_id}")

    image_path = png_path if png_exists else jpg_path

    if image_path.suffix not in {".png", ".jpg"}:
        raise RuntimeError(f"Invalid image extension for item id {item_id}")

    if image_path.name not in {f"{item_id}.png", f"{item_id}.jpg"}:
        raise RuntimeError(f"Invalid image filename for item id {item_id}")

    return image_path


async def spin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    items = context.application.bot_data.get("items")
    if not items:
        raise RuntimeError("Items are not loaded")

    weights = [item["chance"] for item in items]
    selected_item = random.choices(items, weights=weights, k=1)[0]

    image_path = _resolve_item_image_path(selected_item["id"])

    timestamp = datetime.now(timezone.utc).isoformat()
    user = update.effective_user
    chat = update.effective_chat

    user_id = user.id if user is not None else 0
    username = user.username if user is not None and user.username is not None else ""
    chat_id = chat.id if chat is not None else 0

    spin_file = Path("data") / "spin.xlsx"
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
