# app/exchanges/gate.py
from __future__ import annotations

from app.exchanges.base import Offer


class GateProvider:
    name = "gate"

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        # TODO: implement Simple Earn/Flexible once we pick exact endpoint & fields.
        return []