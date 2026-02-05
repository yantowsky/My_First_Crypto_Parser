# app/service.py

import time
from datetime import datetime, timezone

from app.client import BybitClient
from app.config import (
    NORMAL_INTERVAL,
    FAST_INTERVAL,
    FAST_MODE_TTL,
    TESTNET,
    COINS_WHITELIST,
)
from app.notifier import notify
from app.parser import extract_products, detect_new_and_update_state
from app.state import load_state, save_state


class EarnWatcherService:
    def __init__(self):
        self.client = BybitClient(TESTNET)
        self.state = load_state()
        self.fast_until = 0
        self.cycle_count = 0

    def current_interval(self):
        return FAST_INTERVAL if time.time() < self.fast_until else NORMAL_INTERVAL

    def run(self):
        while True:
            self.cycle_count += 1

            now_local = datetime.now()
            now_utc = datetime.now(timezone.utc)
            offset_hours = round((now_local - now_utc.replace(tzinfo=None)).total_seconds() / 3600)
            mode = "FAST" if time.time() < self.fast_until else "NORMAL"

            print(f"\nCycle: {self.cycle_count} | Mode: {mode} | Interval: {self.current_interval()} sec")
            print(f"UTC:   {now_utc.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")
            print(f"Local: {now_local.strftime('%Y-%m-%d %H:%M:%S')} (UTC{offset_hours:+})")

            try:
                data = self.client.fetch_products()
                products = extract_products(data)

                # Console monitor ONLY for whitelist; if whitelist empty -> show nothing about products
                if COINS_WHITELIST:
                    console_products = []
                    for p in products:
                        coin = (p.get("coin") or "").upper()
                        if coin in COINS_WHITELIST:
                            console_products.append(p)

                    if console_products:
                        print(f"\n💎 Console products (whitelist) ({len(console_products)}):")
                        for p in console_products:
                            coin = p.get("coin", "")
                            status = p.get("status", "")
                            product_id = p.get("productId", "")
                            term = p.get("term", 0)
                            term_str = "Flexible" if term == 0 else f"{term} days"
                            category = p.get("category", "Unknown")

                            tiers = p.get("tierAprDetails", [])
                            if tiers:
                                apr_str = tiers[0].get("estimateApr", "N/A")
                            else:
                                apr_str = p.get("estimateApr", "N/A")

                            print(
                                f"    {coin} | APR: {apr_str} | {status} | {term_str} | {category} | productId={product_id}"
                            )

                # ... existing code ...
                if not self.state:
                    detect_new_and_update_state(products, self.state)
                    save_state(self.state)
                    print("\nState initialized (no Telegram alerts on first run)")
                    time.sleep(self.current_interval())
                    continue

                alerts = detect_new_and_update_state(products, self.state)
                if alerts:
                    print(f"\n🔔 Alerts: {len(alerts)} (FAST for {FAST_MODE_TTL} sec)")
                    notify(alerts)
                    self.fast_until = time.time() + FAST_MODE_TTL
                else:
                    print("\nNo alerts")

                save_state(self.state)

            except Exception as e:
                print("❌ ERROR:", e)

            time.sleep(self.current_interval())
