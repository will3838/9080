# Telegram /help Bot

Минимальный многофайловый проект Telegram-бота на `python-telegram-bot` (v20+) с запуском через long polling.

## Установка зависимостей

```bash
python -m pip install -r requirements.txt
```

## Настройка токена

Токен **не коммитится** в репозиторий.

Варианты задания токена:

1. Через переменную окружения `TELEGRAM_BOT_TOKEN`.
2. Через файл `.env` в корне репозитория (автозагрузка):

```env
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
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
