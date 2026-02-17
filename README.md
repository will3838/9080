# Telegram /help Bot

Минимальный многофайловый Telegram-бот на `python-telegram-bot` (v20+) с запуском через **long polling**.

## Установка зависимостей

```bash
python -m pip install -r requirements.txt
```

## Настройка токена

Токен бота **не должен коммититься** в репозиторий.

Можно передать токен одним из способов:

1. Через переменную окружения `TELEGRAM_BOT_TOKEN`.
2. Через файл `.env` в корне проекта (будет автоматически загружен при старте).

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
