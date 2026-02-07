# app/exchanges/bitget.py
from __future__ import annotations

import requests

from app.exchanges.base import Offer


class BitgetProvider:
    name = "bitget"
    _base_url = "https://api.bitget.com"

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        # Bitget Savings Product List [[2]]
        wl = {c.upper() for c in coins_whitelist}
        url = f"{self._base_url}/api/v2/earn/savings/product"
        params = {"filter": "available_and_held"}

        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()

        items = ((data.get("data") or {}).get("list")) or (data.get("data") or [])
        out: list[Offer] = []

        for item in items:
            coin = (item.get("coin") or item.get("baseCoin") or item.get("asset") or "").upper()
            if coin not in wl:
                continue

            apr_raw = item.get("apr") or item.get("maxApr") or item.get("apy")
            apr = None
            if apr_raw is not None:
                try:
                    # usually already percent, but sometimes string "10" / "10.00"
                    apr = float(str(apr_raw).replace("%", "").strip())
                except ValueError:
                    apr = None

            term = item.get("period") or item.get("term") or item.get("duration")
            min_amt = item.get("minAmount") or item.get("minSubscribeAmount")
            max_amt = item.get("maxAmount") or item.get("maxSubscribeAmount") or item.get("quota")

            meta_parts = ["Savings"]
            if term not in ("", None):
                meta_parts.append(f"term={term}")
            if min_amt not in ("", None):
                meta_parts.append(f"min={min_amt}")
            if max_amt not in ("", None):
                meta_parts.append(f"max={max_amt}")

            out.append(Offer(exchange="Bitget", coin=coin, apr=apr, meta=" ".join(meta_parts).strip()))

        return out