#!/bin/bash
# Запуск бота вручную (для тестов, без systemd)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/bot.py"
