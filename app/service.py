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
    EXCHANGES,
)
from app.exchanges import build_providers
from app.notifier import notify
from app.parser import extract_products, detect_new_and_update_state
from app.state import load_state, save_state


class EarnWatcherService:
    def __init__(self):
        self.client = BybitClient(TESTNET)
        self.state = load_state()
        self.fast_until = 0
        self.cycle_count = 0
        self.providers = build_providers(selected=EXCHANGES, testnet=TESTNET)

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
                # === Best APR across exchanges (whitelist only) ===
                if COINS_WHITELIST:
                    offers = []
                    counts_by_provider = {}

                    for provider in self.providers:
                        try:
                            provider_offers = provider.fetch_offers(COINS_WHITELIST)
                            offers.extend(provider_offers)
                            counts_by_provider[provider.name] = len(provider_offers)
                        except Exception as e:
                            counts_by_provider[provider.name] = 0
                            print(f"⚠️  {provider.name}: skipped ({e})")

                    print("\n📊 Offers fetched:", ", ".join(f"{k}={v}" for k, v in counts_by_provider.items()))

                    best_by_coin = {}
                    for o in offers:
                        prev = best_by_coin.get(o.coin)
                        if prev is None or (o.apr is not None and (prev.apr is None or o.apr > prev.apr)):
                            best_by_coin[o.coin] = o

                    if best_by_coin:
                        ranked = sorted(
                            best_by_coin.values(),
                            key=lambda x: (x.apr is not None, x.apr if x.apr is not None else -1),
                            reverse=True,
                        )

                        print("\n🏆 Best APR (whitelist):")
                        header = f"{'COIN':<8} {'APR':>10}  {'EXCHANGE':<10}  CONDITIONS"
                        print(header)
                        print("-" * len(header))

                        for o in ranked:
                            apr_str = f"{o.apr:.4g}%" if o.apr is not None else "N/A"
                            conditions = o.meta or "-"
                            print(f"{o.coin:<8} {apr_str:>10}  {o.exchange:<10}  {conditions}")
                    else:
                        print("\n🏆 Best APR (whitelist): no data (check EXCHANGES and .env creds)")
                else:
                    print("\nℹ️  COINS_WHITELIST is empty -> APR monitor disabled")

                # === Existing Bybit watcher logic (alerts/state/fast mode) ===
                data = self.client.fetch_products()
                products = extract_products(data)

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
