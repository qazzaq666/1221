# Telegram AI Бот (apinex.bond)

Telegram-бот с выбором нейросети и поддержкой фото/видео/аудио, запускаемый как сервис на Linux.

## Функции
- 🤖 Выбор нейросети из списка (кнопки в меню)
- 📸🎥🎤 Поддержка фото, видео, аудио и голосовых сообщений
- 🔄 Автозапуск при загрузке сервера (systemd-сервис)
- 🛠️ Автоустановка зависимостей

## Поддерживаемые модели
```
free/gemini-3.8-flash    free/glm-5.3-flash
free/qwen-3.8-max        free/glm-5.3
free/kimi-k3             free/deepseek-v4-pro-0813
free/deepseek-v4.1-flash free/gpt-6-luna
free/minimax-m3.1-flash  free/glm-5.3-flashx
                         free/jev-1.13
```

## Быстрый старт

### 1. Загрузите файлы на сервер
```bash
# Файлы должны лежать в одной директории: bot.py, install.sh, run.sh, .env.example
```

### 2. Запустите установку
```bash
chmod +x install.sh run.sh
sudo ./install.sh
```

### 3. Настройте конфиг
Отредактируйте `.env`:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
APINEX_API_KEY=ваш_api_ключ
```

> ⚠️ Токен бота берите у @BotFather, API-ключ — у apinex.bond.

### 4. Запустите сервис
```bash
sudo systemctl enable ai-bot
sudo systemctl start ai-bot
sudo systemctl status ai-bot   # проверить статус
```

### 5. Управление
```bash
sudo systemctl stop ai-bot     # остановить
sudo systemctl restart ai-bot  # перезапустить
sudo journalctl -u ai-bot -f   # просмотр логов
```

### 6. Команды бота
- `/start` — меню и выбор модели
- `/models` — переключить нейросеть
- `/help` — инструкция

## Ручной запуск (без systemd)
```bash
./run.sh
```

## Структура
```
hyi/
├── bot.py          # Основной код бота (aiogram 3)
├── install.sh      # Автоустановка + systemd-сервис
├── run.sh          # Запуск вручную
├── .env            # Токены и ключи (НЕ коммитить в git)
├── .env.example    # Шаблон конфига
└── venv/           # Виртуальное окружение (создаётся автоматически)
```

## Зависимости
- Python 3.8+
- aiogram >= 3.0
- python-dotenv
- httpx
