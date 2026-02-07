# app/exchanges/bybit.py
from __future__ import annotations

from app.client import BybitClient
from app.exchanges.base import Offer


class BybitProvider:
    name = "bybit"

    def __init__(self, testnet: bool):
        self.client = BybitClient(testnet)

    @staticmethod
    def _parse_apr_percent(value) -> float | None:
        if value in ("", None):
            return None
        try:
            return float(str(value).replace("%", "").strip())
        except ValueError:
            return None

    @staticmethod
    def _best_tier_apr(tiers: list[dict]) -> tuple[float | None, str]:
        """
        Returns (best_apr_percent, tier_condition_str).
        Condition fields differ between APIs; we try several common keys safely.
        """
        best_apr = None
        best_tier = None

        for t in tiers or []:
            apr = BybitProvider._parse_apr_percent(t.get("estimateApr"))
            if apr is None:
                continue
            if best_apr is None or apr > best_apr:
                best_apr = apr
                best_tier = t

        if best_tier is None:
            return best_apr, ""

        # Try to build a readable tier condition (range/limit)
        min_v = (
            best_tier.get("min")  # <-- NEW (Bybit actual keys)
            or best_tier.get("minAmount")
            or best_tier.get("minStakeAmount")
            or best_tier.get("fromAmount")
            or best_tier.get("lowerLimit")
        )
        max_v = (
            best_tier.get("max")  # <-- NEW (Bybit actual keys)
            or best_tier.get("maxAmount")
            or best_tier.get("maxStakeAmount")
            or best_tier.get("toAmount")
            or best_tier.get("upperLimit")
        )

        if min_v not in ("", None) or max_v not in ("", None):
            left = str(min_v) if min_v not in ("", None) else "0"
            right = str(max_v) if max_v not in ("", None) else "∞"
            return best_apr, f"{left}-{right}"

        tier_id = best_tier.get("tier") or best_tier.get("level") or best_tier.get("id")
        if tier_id not in ("", None):
            return best_apr, f"id={tier_id}"

        return best_apr, "best"

    def fetch_offers(self, coins_whitelist: list[str]) -> list[Offer]:
        data = self.client.fetch_products()
        products = data.get("result", {}).get("list", [])
        wl = {c.upper() for c in coins_whitelist}

        out: list[Offer] = []
        for p in products:
            coin = (p.get("coin") or "").upper()
            if coin not in wl:
                continue

            tiers = p.get("tierAprDetails", []) or []
            best_tier_apr, tier_cond = self._best_tier_apr(tiers)

            apr = best_tier_apr if best_tier_apr is not None else self._parse_apr_percent(p.get("estimateApr"))

            term = p.get("term", 0)
            term_str = "Flexible" if term == 0 else f"{term}d"
            status = p.get("status", "")
            max_stake = p.get("maxStakeAmount", "")

            meta_parts = [term_str]
            if status:
                meta_parts.append(status)
            if tiers:  # show tier info only if tiers exist
                meta_parts.append(f"tier={tier_cond}" if tier_cond else "tier=best")
            if max_stake not in ("", None):
                meta_parts.append(f"max={max_stake}")

            out.append(Offer(exchange="Bybit", coin=coin, apr=apr, meta=" ".join(meta_parts).strip()))
        return out