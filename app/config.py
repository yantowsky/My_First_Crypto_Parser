# app/config.py

import os

from dotenv import load_dotenv

load_dotenv()

# Інтервали
NORMAL_INTERVAL = int(os.getenv("NORMAL_INTERVAL", 300))  # sec
FAST_INTERVAL = int(os.getenv("FAST_INTERVAL", 30))  # sec
FAST_MODE_TTL = int(os.getenv("FAST_MODE_TTL", 600))  # sec

# Продукти
TESTNET = os.getenv("TESTNET", "True").lower() == "true"

COINS_WHITELIST = os.getenv("COINS_WHITELIST", "")
if COINS_WHITELIST.strip():
    COINS_WHITELIST = [c.strip().upper() for c in COINS_WHITELIST.split(",") if c.strip()]
else:
    COINS_WHITELIST = []

# Telegram
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "False").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")