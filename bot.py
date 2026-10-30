#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram AI Бот — apinex.bond
Запуск: python3 bot.py
Сервис: ./install.sh && sudo systemctl start ai-bot
"""

import asyncio
import logging
import os
import sys
import tempfile
import uuid

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Конфигурация — ВСЁ в одном месте, берётся из .env
# ---------------------------------------------------------------------------
load_dotenv()

# --- Telegram ---------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Apinex API -------------------------------------------------------------
APINEX_API_KEY = os.getenv("APINEX_API_KEY")
API_BASE_URL = os.getenv("APINEX_API_URL", "https://api.apinex.bond/v1")
MODEL_LIST = [
    "free/gemini-3.8-flash",
    "free/qwen-3.8-max",
    "free/kimi-k3",
    "free/deepseek-v4.1-flash",
    "free/glm-5.3-flash",
    "free/minimax-m3.1-flash",
    "free/glm-5.3",
    "free/deepseek-v4-pro-0813",
    "free/gpt-6-luna",
    "free/glm-5.3-flashx",
    "free/jev-1.13",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Заглушки для aiogram (если не установлен) ------------------------------
try:
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.filters import Command
    from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
    from aiogram.utils import markdown
    AIogram_AVAILABLE = True
except ImportError:
    AIogram_AVAILABLE = False
    logger.warning("⚠️ aiogram не установлен — бот не запустится. Установите: pip install aiogram python-dotenv httpx")


# ---------------------------------------------------------------------------
# Хелперы
# ---------------------------------------------------------------------------
def get_model_display(model: str) -> str:
    """Красивое имя модели для кнопок."""
    short = model.replace("free/", "")
    name_map = {
        "gemini-3.8-flash": "Gemini Flash",
        "qwen-3.8-max": "Qwen Max",
        "kimi-k3": "Kimi K3",
        "deepseek-v4.1-flash": "DeepSeek Flash",
        "glm-5.3-flash": "GLM Flash",
        "minimax-m3.1-flash": "MiniMax Flash",
        "glm-5.3": "GLM",
        "deepseek-v4-pro-0813": "DeepSeek Pro",
        "gpt-6-luna": "GPT-6 Luna",
        "glm-5.3-flashx": "GLM FlashX",
        "jev-1.13": "Jev 1.13",
    }
    return name_map.get(short, short)


# ---------------------------------------------------------------------------
# Команды
# ---------------------------------------------------------------------------
async def send_menu(message) -> None:
    """Отправить меню с выбором модели."""
    if not AIogram_AVAILABLE:
        return
    keyboard = []
    for m in MODEL_LIST:
        keyboard.append([InlineKeyboardButton(text=f"🤖 {get_model_display(m)}", callback_data=f"model:{m}")])
    await message.answer(
        markdown.markdown(
            f"👋 Привет, {message.from_user.first_name}!\n"
            f"Я AI-ассистент, подключённый к нейросетям через кастомный API.\n\n"
            f"Выберите модель для общения:"
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


if AIogram_AVAILABLE:
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message) -> None:
        await send_menu(message)

    @dp.message(Command("models"))
    async def cmd_models(message) -> None:
        await send_menu(message)

    @dp.callback_query()
    async def callback_model(call) -> None:
        if call.data.startswith("model:"):
            model = call.data.split(":", 1)[1]
            await call.message.answer(f"✅ Модель выбрана: <code>{model}</code>")
            await bot.answer_callback_query(call.id)

    @dp.message(Command("help"))
    async def cmd_help(message) -> None:
        await message.answer(
            markdown.markdown(
                "📖 <b>Инструкция</b>\n\n"
                "• Пиши сообщения — получаешь ответ от выбранной нейросети\n"
                "• Прикрепляй <b>фото</b>, <b>видео</b> или <b>аудио</b> (включая голосовые)\n"
                "• <code>/models</code> — выбрать другую нейросеть\n"
                "• <code>/start</code> — перезапустить меню"
            )
        )

    # Обработка медиа — универсальный хендлер
    @dp.message(F := __import__("aiogram.filters", fromlist=["F"]).F)
    async def handle_media(message) -> None:
        media_type = None
        file_id = None
        caption = ""
        if message.photo:
            file_id = message.photo[-1].file_id
            media_type = "photo"
        elif message.video:
            file_id = message.video.file_id
            media_type = "video"
        elif message.voice:
            file_id = message.voice.file_id
            caption = "🎤 Голосовое сообщение"
            media_type = "voice"
        elif message.audio:
            file_id = message.audio.file_id
            media_type = "audio"
        if file_id and media_type:
            await chat_with_media(message, caption or None, file_id, media_type)

    @dp.message()
    async def handle_text(message) -> None:
        try:
            response = await call_ai_api(message.text, None, None)
            await message.answer(str(response), parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            logger.exception("Ошибка при обработке сообщения")
            await message.answer(f"❌ Ошибка: {e}")


# ---------------------------------------------------------------------------
# Обработка медиа
# ---------------------------------------------------------------------------
async def chat_with_media(message, caption, file_id, media_type) -> None:
    if caption:
        await message.answer(f"⏳ Обработка {caption}...")
    local_path = await download_file(file_id)
    try:
        response = await call_ai_api(message.text, local_path, media_type)
        await message.answer(str(response), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.exception("Ошибка при обработке медиа")
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        try:
            os.remove(local_path)
        except Exception:
            pass


async def download_file(file_id: str) -> str:
    """Скачать файл из Telegram в временную папку."""
    file_info = await bot.get_file(file_id)
    downloaded = await bot.download_file(file_info.file_path)
    suffix = os.path.splitext(file_info.file_path)[1] or ".bin"
    temp_dir = os.path.join(tempfile.gettempdir(), "ai_bot")
    os.makedirs(temp_dir, exist_ok=True)
    local_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{suffix}")
    with open(local_path, "wb") as f:
        f.write(downloaded)
    return local_path


# ---------------------------------------------------------------------------
# API к apinex.bond
# ---------------------------------------------------------------------------
async def call_ai_api(prompt: str, file_path: str | None, media_type: str | None) -> str:
    """Вызывает API https://api.apinex.bond/v1 ."""
    import httpx

    headers = {
        "Authorization": f"Bearer {APINEX_API_KEY}",
        "User-Agent": "ai-bot/1.0",
    }

    # Текущая выбранная модель (заглушка — можно сохранять в базе/памяти)
    selected_model = "free/gpt-6-luna"

    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {"model": selected_model, "prompt": prompt or f"Обработай этот {media_type}"}
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{API_BASE_URL}/chat/completions",
                    headers=headers,
                    data=data,
                    files=files,
                )
    else:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{API_BASE_URL}/chat/completions",
                headers=headers,
                json={"model": selected_model, "prompt": prompt},
            )

    resp.raise_for_status()
    content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", resp.text)
    return content


# ---------------------------------------------------------------------------
# Запуск
# ---------------------------------------------------------------------------
async def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен в .env")
        sys.exit(1)
    if not APINEX_API_KEY:
        logger.error("❌ APINEX_API_KEY не установлен в .env")
        sys.exit(1)
    if not AIogram_AVAILABLE:
        logger.error("❌ aiogram не установлен")
        sys.exit(1)

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать общение"),
        BotCommand(command="models", description="Выбрать нейросеть"),
        BotCommand(command="help", description="Помощь"),
    ])

    logger.info("🚀 Бот запущен, токены проверены")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
