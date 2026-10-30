#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import py_compile
import sys

print("============================================================")
print("TECH CHECK: test_bot.py (without real API)")
print("============================================================")

from dotenv import load_dotenv
load_dotenv()
print("")
print("1. Loading .env:")
print("   TELEGRAM_BOT_TOKEN: " + ("OK" if os.getenv("TELEGRAM_BOT_TOKEN") else "MISSING"))
print("   APINEX_API_KEY:     " + ("OK" if os.getenv("APINEX_API_KEY") else "MISSING"))
print("   APINEX_API_URL:     " + (os.getenv("APINEX_API_URL", "N/A") or "N/A"))

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
print("")
print("2. Number of models: " + str(len(MODEL_LIST)))
for i, m in enumerate(MODEL_LIST, 1):
    print("   %2d. %s" % (i, m))

try:
    py_compile.compile('bot.py', doraise=True)
    print("")
    print("3. bot.py compiles: OK")
except py_compile.PyCompileError as e:
    print("")
    print("3. bot.py compile ERROR: " + str(e))

print("")
print("4. Dependencies:")
for lib in ["aiogram", "dotenv", "httpx"]:
    try:
        __import__(lib)
        print("   %s: OK" % lib)
    except ImportError:
        print("   %s: MISSING" % lib)

print("")
print("============================================================")
print("TEST FINISHED")
print("============================================================")
