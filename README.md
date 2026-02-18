# Telegram /help Bot

Минимальный Telegram-бот на `python-telegram-bot` (v20+) с запуском через long polling.

## Установка зависимостей

```bash
python -m pip install -r requirements.txt
```

## Настройка токена

Токен **не хранится в коде** и не должен коммититься в репозиторий.

Можно задать токен двумя способами:

1. Через переменную окружения `TELEGRAM_BOT_TOKEN`.
2. Через файл `.env` в корне репозитория (рядом с `README.md`).

Пример `.env`:

```env
TELEGRAM_BOT_TOKEN="PASTE_YOUR_TOKEN_HERE"
```

## Запуск

### Linux / Mac

```bash
PYTHONPATH=src python -m bot.main
```

### Windows PowerShell

```powershell
$env:PYTHONPATH="src"; python -m bot.main
```

## Команды бота

Поддерживается только команда `/help`.
