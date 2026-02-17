"""Handler for /captcha command."""

from __future__ import annotations

import random

from telegram import Update
from telegram.ext import ContextTypes


def generate_captcha() -> tuple[str, int]:
    while True:
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        op = random.choice(["+", "-"])

        if op == "+":
            answer = a + b
        else:
            if a <= b:
                continue
            answer = a - b

        if answer <= 0:
            continue

        return f"{a}{op}{b}=?", answer


async def captcha_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    user = update.effective_user
    user_id = user.id if user is not None else 0

    pending = context.application.bot_data.setdefault("captcha_pending", {})
    state = pending.get(user_id)

    if state is None:
        await update.message.reply_text("капча не требуется")
        return

    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Неверный формат. Используй: /captcha <число>")
        return

    try:
        user_answer = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Неверный формат. Используй: /captcha <число>")
        return

    if user_answer != state["answer"]:
        question, answer = generate_captcha()
        pending[user_id] = {"question": question, "answer": answer}
        await update.message.reply_text(
            f"неверно, попробуй ещё. Капча: {question} Ответь командой: /captcha <число>"
        )
        return

    pending.pop(user_id, None)
    await update.message.reply_text("капча пройдена")
