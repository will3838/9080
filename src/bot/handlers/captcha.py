"""Handler for /captcha command."""

from __future__ import annotations

import random

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


async def captcha_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    user = update.effective_user
    user_id = user.id if user is not None else 0

    captcha_pending = context.application.bot_data.setdefault("captcha_pending", {})
    current = captcha_pending.get(user_id)

    if current is None:
        await update.message.reply_text("капча не требуется")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Неверный формат. Используй: /captcha <число>")
        return

    try:
        answer = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Неверный формат. Используй: /captcha <число>")
        return

    if answer != current["answer"]:
        question, correct_answer = generate_captcha()
        captcha_pending[user_id] = {"question": question, "answer": correct_answer}
        await update.message.reply_text(
            f"неверно, попробуй ещё. Капча: {question} Ответь командой: /captcha <число>"
        )
        return

    captcha_pending.pop(user_id, None)
    await update.message.reply_text("капча пройдена")
