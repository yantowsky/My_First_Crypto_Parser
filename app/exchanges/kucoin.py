# app/exchanges/kucoin.py
from __future__ import annotations

from app.exchanges.base import Offer


class KucoinProvider:
    name = "kucoin"

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        # TODO: implement Earn Flexible once we pick exact endpoint & fields.
        return []