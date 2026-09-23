from __future__ import annotations

from desk_radar.config import Settings
from desk_radar.models import FilterVerdict, PairSnapshot

ALLOWED_QUOTES = {
    "base": {"WETH", "USDC", "USDT", "ETH"},
    "solana": {"SOL", "USDC", "USDT", "WSOL"},
}


def evaluate(pair: PairSnapshot, settings: Settings) -> FilterVerdict:
    reasons: list[str] = []
    chain = pair.chain.lower()
    if chain not in settings.chains:
        reasons.append(f"chain={pair.chain}")
    quotes = ALLOWED_QUOTES.get(chain, set())
    if pair.quote_symbol.upper() not in quotes:
        reasons.append(f"quote={pair.quote_symbol}")
    if pair.liquidity_usd < settings.min_liq_usd:
        reasons.append(f"liq={pair.liquidity_usd:.0f}<{settings.min_liq_usd:.0f}")
    if pair.volume_5m_usd < settings.min_vol_5m:
        reasons.append(f"vol5m={pair.volume_5m_usd:.0f}<{settings.min_vol_5m:.0f}")
    age = pair.age_minutes
    if age is None:
        reasons.append("age=unknown")
    else:
        if age < settings.min_age_min:
            reasons.append(f"too_new={age:.1f}m")
        if age > settings.max_age_hours * 60:
            reasons.append(f"too_old={age / 60:.1f}h")
    if pair.price_usd <= 0:
        reasons.append("price<=0")
    return FilterVerdict(pair=pair, accepted=not reasons, reasons=reasons)
