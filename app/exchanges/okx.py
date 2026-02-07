# app/exchanges/okx.py
from __future__ import annotations

from app.exchanges.base import Offer


class OkxProvider:
    name = "okx"

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        # TODO: implement Simple Earn/Savings once we pick the exact OKX endpoint & fields.
        return []