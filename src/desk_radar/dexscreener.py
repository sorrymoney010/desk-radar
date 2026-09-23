from __future__ import annotations

from typing import Any

from desk_radar.config import Settings
from desk_radar.http import get_json
from desk_radar.models import PairSnapshot


def _num(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def parse_pair(raw: dict[str, Any]) -> PairSnapshot | None:
    chain = str(raw.get("chainId") or "")
    base = raw.get("baseToken") or {}
    quote = raw.get("quoteToken") or {}
    liq = raw.get("liquidity") or {}
    vol = raw.get("volume") or {}
    pair_addr = str(raw.get("pairAddress") or "")
    base_addr = str(base.get("address") or "")
    if not pair_addr or not base_addr:
        return None
    created = raw.get("pairCreatedAt")
    created_ms = int(created) if created else None
    return PairSnapshot(
        chain=chain,
        pair_address=pair_addr,
        base_address=base_addr,
        base_symbol=str(base.get("symbol") or "?"),
        quote_symbol=str(quote.get("symbol") or "?"),
        price_usd=_num(raw.get("priceUsd")),
        liquidity_usd=_num(liq.get("usd")),
        volume_5m_usd=_num(vol.get("m5")),
        pair_created_at_ms=created_ms,
        url=str(raw.get("url") or ""),
    )


class DexScreener:
    def __init__(self, settings: Settings, fetcher=None) -> None:
        self.settings = settings
        self._fetcher = fetcher or get_json

    def _get(self, path: str) -> Any:
        return self._fetcher(f"{self.settings.dexscreener_base}{path}")

    def search_chain(self, query: str) -> list[PairSnapshot]:
        payload = self._get(f"/latest/dex/search?q={query}")
        return [snap for raw in (payload.get("pairs") or []) if (snap := parse_pair(raw))]

    def token_pairs(self, address: str) -> list[PairSnapshot]:
        payload = self._get(f"/latest/dex/tokens/{address}")
        return [snap for raw in (payload.get("pairs") or []) if (snap := parse_pair(raw))]

    def token_profiles(self) -> list[dict[str, Any]]:
        payload = self._get("/token-profiles/latest/v1")
        if isinstance(payload, list):
            return payload
        return payload.get("profiles") or payload.get("data") or []

    def token_boosts(self) -> list[dict[str, Any]]:
        payload = self._get("/token-boosts/latest/v1")
        if isinstance(payload, list):
            return payload
        return payload.get("boosts") or payload.get("data") or []
