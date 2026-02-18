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
    total_items = 0
    total_value = 0

    for item_id, count in rows:
        item = items_by_id.get(item_id)
        if item is None:
            continue
        name = str(item["name"])
        price = int(item["price"])
        chance = float(item["chance"])
        visible_rows.append((item_id, count, name, price, chance))
        total_items += count
        total_value += price * count

    unique_items = len(visible_rows)

    if unique_items == 0:
        text = "Инвентарь пуст.\n\nУникальных предметов: 0\nВсего предметов: 0\nСуммарная стоимость: 0 метровалюта"
        return text, None

    total_pages = (unique_items - 1) // PAGE_SIZE + 1
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_rows = visible_rows[start:end]

    lines = [
        f"{name} x{count} | цена {price} метровалюта | шанс {chance}"
        for _, count, name, price, chance in page_rows
    ]
    lines.append("")
    lines.append(f"Уникальных предметов: {unique_items}")
    lines.append(f"Всего предметов: {total_items}")
    lines.append(f"Суммарная стоимость: {total_value} метровалюта")
    text = "\n".join(lines)

    markup = None
    if total_pages > 1:
        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton("◀️", callback_data=f"inv:{user_id}:{page - 1}"))
        if page < total_pages - 1:
            buttons.append(InlineKeyboardButton("▶️", callback_data=f"inv:{user_id}:{page + 1}"))
        markup = InlineKeyboardMarkup([buttons]) if buttons else None

    return text, markup


async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    user = update.effective_user
    user_id = user.id if user is not None else 0
    text, markup = render_inventory_page(user_id, 0, context)
    await update.message.reply_text(text, reply_markup=markup)


async def inventory_text_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return
    if update.message.text not in {"инв", "инвентарь"}:
        return

    user = update.effective_user
    user_id = user.id if user is not None else 0
    text, markup = render_inventory_page(user_id, 0, context)
    await update.message.reply_text(text, reply_markup=markup)


async def inventory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is None:
        return

    query = update.callback_query

    data = query.data or ""
    parts = data.split(":")
    if len(parts) != 3:
        return

    _, owner_user_id_str, page_str = parts

    try:
        owner_user_id = int(owner_user_id_str)
        page = int(page_str)
    except ValueError:
        return

    current_user = update.effective_user
    current_user_id = current_user.id if current_user is not None else 0

    if current_user_id != owner_user_id:
        await query.answer("не твой инвентарь")
        return

    await query.answer()
    text, markup = render_inventory_page(owner_user_id, page, context)
    await query.edit_message_text(text=text, reply_markup=markup)
