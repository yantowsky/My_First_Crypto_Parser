# app/exchanges/binance.py
from __future__ import annotations

import requests

from app.config import BINANCE_API_KEY, BINANCE_API_SECRET
from app.exchanges.base import Offer
from app.exchanges.http import binance_signed_params


class BinanceProvider:
    name = "binance"
    _base_url = "https://api.binance.com"

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        # Signed USER_DATA endpoint [[1]](https://developers.binance.com/docs/simple_earn/flexible-locked/account/Get-Simple-Earn-Flexible-Product-List)
        if not BINANCE_API_KEY or not BINANCE_API_SECRET:
            return []

        wl = {c.upper() for c in coins_whitelist}
        out: list[Offer] = []

        headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
        # paginate to cover more than default size
        current = 1
        size = 100

        while True:
            params = binance_signed_params({"current": current, "size": size}, api_secret=BINANCE_API_SECRET)
            url = f"{self._base_url}/sapi/v1/simple-earn/flexible/list"
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()

            rows = data.get("rows", []) or []
            for row in rows:
                coin = (row.get("asset") or "").upper()
                if coin not in wl:
                    continue

                tier_apr_map = row.get("tierAnnualPercentageRate") or {}
                best_tier_label = None
                best_tier_rate = None

                if isinstance(tier_apr_map, dict) and tier_apr_map:
                    for tier_label, rate in tier_apr_map.items():
                        try:
                            rate_f = float(rate)
                        except (TypeError, ValueError):
                            continue
                        if best_tier_rate is None or rate_f > best_tier_rate:
                            best_tier_rate = rate_f
                            best_tier_label = str(tier_label)

                if best_tier_rate is not None:
                    apr = best_tier_rate * 100.0
                else:
                    apr_raw = row.get("latestAnnualPercentageRate")
                    try:
                        apr = float(apr_raw) * 100.0 if apr_raw is not None else None
                    except (TypeError, ValueError):
                        apr = None

                status = row.get("status")  # PREHEATING/PURCHASING/END
                can_purchase = row.get("canPurchase")
                is_sold_out = row.get("isSoldOut")
                min_amt = row.get("minPurchaseAmount")
                product_id = row.get("productId")

                meta_parts = ["Flexible"]
                if status:
                    meta_parts.append(str(status))
                if best_tier_label:
                    meta_parts.append(f"tier={best_tier_label}")
                if can_purchase is not None:
                    meta_parts.append(f"canBuy={can_purchase}")
                if is_sold_out is not None:
                    meta_parts.append(f"soldOut={is_sold_out}")
                if min_amt not in ("", None):
                    meta_parts.append(f"min={min_amt}")
                if product_id not in ("", None):
                    meta_parts.append(f"id={product_id}")

                out.append(Offer(exchange="Binance", coin=coin, apr=apr, meta=" ".join(meta_parts).strip()))

            if len(rows) < size:
                break
            current += 1

        return out