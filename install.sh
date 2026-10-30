#!/bin/bash
# ==============================================================================
# install.sh — автоматическая установка Telegram AI бота (apinex.bond)
# ВСЯ КОНФИГУРАЦИЯ — В ОДНОМ ФАЙЛЕ .env
# ==============================================================================
set -e

echo "🔧 Установка Telegram AI бота на Linux..."

# --- 1. Проверка Python ------------------------------------------------------
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ Python: $PYTHON_VERSION"

# --- 2. Создание виртуального окружения --------------------------------------
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
fi

# --- 3. Установка зависимостей ------------------------------------------------
echo "📦 Установка зависимостей (aiogram, python-dotenv, httpx)..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -q \
    "aiogram>=3.0" \
    "python-dotenv>=1.0" \
    "httpx>=0.25"

# --- 4. Создание файла конфигурации .env (одна строка на параметр) -----------
ENV_FILE="$PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "🔑 Создание файла конфигурации .env..."
    cat > "$ENV_FILE" << 'EOF'
# ==============================================================================
# Telegram AI Бот — КОНФИГУРАЦИЯ
# Все ключи и токены задаются ТОЛЬКО ЗДЕСЬ, один раз.
#
# ВАРИАНТ 1: Заполните строки ниже вашими значениями (удалите текст после =):
#   TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
#   APINEX_API_KEY=ваш_api_ключ
#
# ВАРИАНТ 2: Если хотите вставить ключи прямо сейчас, замените содержимое
# файла на ваши значения, например:
#   TELEGRAM_BOT_TOKEN=9287765709:AAGpkdRi47aBWSb85WO4MMTXsyXZSyuyTS0
#   APINEX_API_KEY=sk-apx7ca8a73b9ae26919e14fa5a56b490cb02645cf62acbe931
#
# Базовый URL API (можно менять, по умолчанию apinex.bond)
APINEX_API_URL=https://api.apinex.bond/v1
EOF
    chmod 600 "$ENV_FILE"
    echo "⚠️  Файл .env создан. Отредактируйте его и вставьте токены:"
    echo "     nano .env"
    echo "     (или откройте в любом текстовом редакторе)"
else
    echo "ℹ️  $ENV_FILE уже существует"
fi

# --- 5. Создание systemd-сервиса -----------------------------------------------
SERVICE_NAME="ai-bot"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

if [ "$(id -u)" -ne 0 ]; then
    echo "⚠️  Запустите скрипт через sudo для создания systemd-сервиса"
else
    echo "📝 Создание systemd-сервиса ($SERVICE_NAME)..."
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Telegram AI Bot (apinex.bond)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    chmod 644 "$SERVICE_FILE"
    echo "🔄 Перезагрузка daemon systemd..."
    systemctl daemon-reload
fi

# --- 6. Готово ------------------------------------------------------------------
echo ""
echo "🎉 Установка завершена!"
echo ""
echo "=== Дальнейшие шаги ==="
echo "1. Вставьте токены в .env (ТОЛЬКО ОДИН ФАЙЛ):"
echo "     nano .env"
echo "     👉 TELEGRAM_BOT_TOKEN=9287765709:AAGpkdRi47aBWSb85WO4MMTXsyXZSyuyTS0"
echo "     👉 APINEX_API_KEY=sk-apx7ca8a73b9ae26919e14fa5a56b490cb02645cf62acbe931"
echo "2. Запуск сервиса (если root):"
echo "     sudo systemctl enable ai-bot"
echo "     sudo systemctl start ai-bot"
echo "     sudo systemctl status ai-bot"
echo ""
echo "   ИЛИ ручной запуск:"
echo "     ./run.sh"
echo ""
