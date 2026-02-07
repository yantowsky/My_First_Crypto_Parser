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

# Exchanges (comma-separated). Default keeps current behavior (Bybit only).
EXCHANGES = os.getenv("EXCHANGES", "bybit")
EXCHANGES = [e.strip().lower() for e in EXCHANGES.split(",") if e.strip()]

# Optional creds (needed only for some exchanges, e.g. Binance Simple Earn is signed USER_DATA)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Telegram
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "False").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")