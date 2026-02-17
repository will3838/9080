# Telegram /help Bot

Минимальный многофайловый Telegram-бот на `python-telegram-bot` (v20+) с поддержкой загрузки токена из переменных окружения и `.env`.

## Установка зависимостей

```bash
python -m pip install -r requirements.txt
```

## Настройка токена

Токен бота **не хранится в коде и не коммитится**.

Можно задать его одним из способов:

1. Через переменную окружения `TELEGRAM_BOT_TOKEN`.
2. Через файл `.env` в корне проекта (рядом с `README.md`).

Пример `.env`:

```env
TELEGRAM_BOT_TOKEN="PASTE_YOUR_TOKEN_HERE"
```

## Запуск

Linux / Mac:

```bash
PYTHONPATH=src python -m bot.main
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m bot.main
```

## Поддерживаемая команда

- `/help` (включая `/help@MyBot`) → `автор @HATE_death_ME`
