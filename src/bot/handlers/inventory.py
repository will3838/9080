"""Handlers for user inventory."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.storage.inventory_db import get_inventory_rows

PAGE_SIZE = 25


def render_inventory_page(user_id: int, page: int, context: ContextTypes.DEFAULT_TYPE) -> tuple[str, InlineKeyboardMarkup | None]:
    rows = get_inventory_rows(user_id)
    items = context.application.bot_data.get("items", [])
    items_by_id = {item["id"]: item for item in items}

    visible_rows: list[tuple[int, int, str, int, float]] = []
    total_unique = 0
    total_count = 0
    total_price = 0

    for item_id, count in rows:
        item = items_by_id.get(item_id)
        if item is None:
            continue
        visible_rows.append((item_id, count, item["name"], item["price"], item["chance"]))
        total_unique += 1
        total_count += count
        total_price += item["price"] * count

    total_pages = max(1, (len(visible_rows) + PAGE_SIZE - 1) // PAGE_SIZE)
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_rows = visible_rows[start:end]

    lines = []
    for _, count, name, price, chance in page_rows:
        lines.append(f"{name} x{count} | цена {price} метровалюта | шанс {chance}")

    if not lines:
        lines.append("Инвентарь пуст.")

    lines.append("")
    lines.append(f"Уникальных предметов: {total_unique}")
    lines.append(f"Всего предметов: {total_count}")
    lines.append(f"Суммарная стоимость: {total_price} метровалюта")

    keyboard = []
    if total_pages > 1:
        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton("◀️", callback_data=f"inv:{user_id}:{page - 1}"))
        if page < total_pages - 1:
            buttons.append(InlineKeyboardButton("▶️", callback_data=f"inv:{user_id}:{page + 1}"))
        if buttons:
            keyboard.append(buttons)

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    return "\n".join(lines), reply_markup


async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    user = update.effective_user
    user_id = user.id if user is not None else 0
    text, reply_markup = render_inventory_page(user_id, 0, context)
    await update.message.reply_text(text, reply_markup=reply_markup)


async def inventory_text_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    if update.message.text not in {"инв", "инвентарь"}:
        return

    user = update.effective_user
    user_id = user.id if user is not None else 0
    text, reply_markup = render_inventory_page(user_id, 0, context)
    await update.message.reply_text(text, reply_markup=reply_markup)


async def inventory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        return

    parts = query.data.split(":")
    if len(parts) != 3:
        await query.answer()
        return

    _, owner_user_id_str, page_str = parts

    try:
        owner_user_id = int(owner_user_id_str)
        page = int(page_str)
    except ValueError:
        await query.answer()
        return

    user = update.effective_user
    caller_user_id = user.id if user is not None else 0

    if caller_user_id != owner_user_id:
        await query.answer("не твой инвентарь")
        return

    text, reply_markup = render_inventory_page(owner_user_id, page, context)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    await query.answer()
