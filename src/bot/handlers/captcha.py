"""Captcha generation and answer handler."""

from __future__ import annotations

import random
import re

from telegram import Update
from telegram.ext import ContextTypes


def generate_captcha() -> tuple[str, int]:
    operation = random.choice(["+", "-"])
    a = random.randint(1, 9)
    b = random.randint(1, 9)

    if operation == "-":
        while a <= b:
            a = random.randint(1, 9)
            b = random.randint(1, 9)
        answer = a - b
    else:
        answer = a + b

    return f"{a}{operation}{b}=?", answer


async def captcha_answer_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    user = update.effective_user
    user_id = user.id if user is not None else 0

    captcha_pending = context.application.bot_data.setdefault("captcha_pending", {})
    current = captcha_pending.get(user_id)
    if current is None:
        return

    text = update.message.text
    if text.startswith("/"):
        return

    if re.fullmatch(r"^\d+$", text) is None:
        return

    answer = int(text)
    if answer != current["answer"]:
        question, correct_answer = generate_captcha()
        captcha_pending[user_id] = {"question": question, "answer": correct_answer}
        await update.message.reply_text(f"неверно, попробуй ещё.\nКапча: {question} Ответь числом.")
        return

    captcha_pending.pop(user_id, None)
    spin_counts = context.application.bot_data.setdefault("spin_counts", {})
    spin_counts[user_id] = 0
    await update.message.reply_text("капча пройдена, можешь снова использовать /spin")
