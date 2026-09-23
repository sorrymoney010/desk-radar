from __future__ import annotations

import math

from desk_radar.config import Settings
from desk_radar.dexscreener import DexScreener
from desk_radar.models import PairSnapshot

SEARCH_QUERIES = {
    "base": ("base", "WETH base", "USDC base"),
    "solana": ("solana", "SOL", "USDC solana"),
}

ALLOWED_QUOTES = {
    "base": {"WETH", "USDC", "USDT", "ETH"},
    "solana": {"SOL", "USDC", "USDT", "WSOL"},
}


def quality_score(pair: PairSnapshot) -> float:
    age = pair.age_minutes or 60
    age = max(age, 1.0)
    liq = max(pair.liquidity_usd, 1.0)
    return (pair.volume_5m_usd * math.log10(liq + 10)) / age


def _allowed(pair: PairSnapshot, chains: tuple[str, ...]) -> bool:
    chain = pair.chain.lower()
    if chain not in chains:
        return False
    quotes = ALLOWED_QUOTES.get(chain, set())
    return pair.quote_symbol.upper() in quotes


class Discovery:
    def __init__(self, settings: Settings, dex: DexScreener | None = None) -> None:
        self.settings = settings
        self.dex = dex or DexScreener(settings)

    def harvest(self) -> list[PairSnapshot]:
        seen: dict[str, PairSnapshot] = {}
        for chain in self.settings.chains:
            for query in SEARCH_QUERIES.get(chain, (chain,)):
                try:
                    found = self.dex.search_chain(query)
                except RuntimeError:
                    found = []
                for snap in found:
                    if not _allowed(snap, self.settings.chains):
                        continue
                    key = f"{snap.chain}:{snap.pair_address.lower()}"
                    prev = seen.get(key)
                    if prev is None or snap.volume_5m_usd > prev.volume_5m_usd:
                        seen[key] = snap
            self._ingest_profiles(chain, seen)
        ranked = sorted(seen.values(), key=quality_score, reverse=True)
        return ranked[: self.settings.max_candidates]

    def _ingest_profiles(self, chain: str, seen: dict[str, PairSnapshot]) -> None:
        try:
            profiles = self.dex.token_profiles()
        except RuntimeError:
            return
        addresses: list[str] = []
        for row in profiles:
            row_chain = str(row.get("chainId") or row.get("chain") or "").lower()
            if row_chain and row_chain != chain:
                continue
            addr = str(row.get("tokenAddress") or row.get("address") or "")
            if addr:
                addresses.append(addr)
        for addr in addresses[:15]:
            try:
                pairs = self.dex.token_pairs(addr)
            except RuntimeError:
                continue
            for snap in pairs:
                if not _allowed(snap, self.settings.chains):
                    continue
                key = f"{snap.chain}:{snap.pair_address.lower()}"
                prev = seen.get(key)
                if prev is None or snap.volume_5m_usd > prev.volume_5m_usd:
                    seen[key] = snap

    def refresh(self, address: str) -> list[PairSnapshot]:
        try:
            return [s for s in self.dex.token_pairs(address) if _allowed(s, self.settings.chains)]
        except RuntimeError:
            return []
