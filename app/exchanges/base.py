# app/exchanges/base.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Offer:
    exchange: str
    coin: str
    apr: float | None
    meta: str = ""  # term/limits/status/etc


class ExchangeProvider(Protocol):
    name: str

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        raise NotImplementedError