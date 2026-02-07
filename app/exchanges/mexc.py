# app/exchanges/mexc.py
from __future__ import annotations

from app.exchanges.base import Offer


class MexcProvider:
    name = "mexc"

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        # TODO: implement Flexible/Savings once we pick exact endpoint & fields.
        return []