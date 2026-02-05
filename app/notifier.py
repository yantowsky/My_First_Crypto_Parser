# app/notifier.py

import requests

from app.config import TELEGRAM_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BYBIT_EARN_URL = "https://www.bybit.com/earn"


def _extract_apr_percent(p: dict) -> float | None:
    # Bybit може віддавати APR або в tierAprDetails, або в estimateApr
    tiers = p.get("tierAprDetails", [])
    if tiers:
        apr_str = tiers[0].get("estimateApr", None)
    else:
        apr_str = p.get("estimateApr", None)

    if not apr_str:
        return None

    try:
        return float(str(apr_str).replace("%", "").strip())
    except ValueError:
        return None


def notify(products: list):
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    for p in products:
        send_telegram(format_product_message(p))


def format_product_message(p: dict) -> str:
    product_id = p.get("productId", "")
    coin = p.get("coin", "")
    status = p.get("status", "")
    term = p.get("term", 0)
    term_str = "Flexible" if term == 0 else f"{term} days"
    category = p.get("category", "")
    max_stake = p.get("maxStakeAmount", "")

    apr = _extract_apr_percent(p)
    apr_line = f"APR: <b>{apr}%</b>\n" if apr is not None else "APR: <b>N/A</b>\n"

    message = (
        f"🔥 <b>NEW PRODUCT / AVAILABLE</b>\n"
        f"productId: <b>{product_id}</b>\n"
        f"Coin: <b>{coin}</b>\n"
        f"Status: <b>{status}</b>\n"
        f"{apr_line}"
        f"Term: {term_str}\n"
        f"Category: {category}\n"
    )

    if max_stake:
        message += f"Max Stake: {max_stake}\n"

    message += f"\n🔗 <a href=\"{BYBIT_EARN_URL}\">Open Bybit Earn</a>"

    return message


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print("Telegram error:", response.text)
    except Exception as e:
        print("Telegram exception:", e)
