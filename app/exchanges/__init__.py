# app/exchanges/__init__.py
from __future__ import annotations

from app.exchanges.base import ExchangeProvider
from app.exchanges.bybit import BybitProvider
from app.exchanges.binance import BinanceProvider
from app.exchanges.bitget import BitgetProvider
from app.exchanges.gate import GateProvider
from app.exchanges.kucoin import KucoinProvider
from app.exchanges.mexc import MexcProvider
from app.exchanges.okx import OkxProvider


def build_providers(selected: list[str], testnet: bool) -> list[ExchangeProvider]:
    mapping = {
        "bybit": lambda: BybitProvider(testnet=testnet),
        "binance": lambda: BinanceProvider(),
        "bitget": lambda: BitgetProvider(),
        "okx": lambda: OkxProvider(),
        "mexc": lambda: MexcProvider(),
        "gate": lambda: GateProvider(),
        "kucoin": lambda: KucoinProvider(),
    }

    providers: list[ExchangeProvider] = []
    for name in selected:
        factory = mapping.get(name)
        if factory:
            providers.append(factory())
    return providers