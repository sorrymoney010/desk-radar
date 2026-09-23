from desk_radar.config import Settings
from desk_radar.filters import evaluate
from desk_radar.models import PairSnapshot


def _pair(**kwargs) -> PairSnapshot:
    data = dict(
        chain="base",
        pair_address="0xpair",
        base_address="0xbase",
        base_symbol="TEST",
        quote_symbol="WETH",
        price_usd=0.001,
        liquidity_usd=50_000,
        volume_5m_usd=10_000,
        pair_created_at_ms=1_700_000_000_000,
    )
    data.update(kwargs)
    return PairSnapshot(**data)


def test_rejects_low_liquidity():
    settings = Settings(min_liq_usd=15_000)
    verdict = evaluate(_pair(liquidity_usd=100), settings)
    assert verdict.accepted is False
    assert any("liq=" in r for r in verdict.reasons)


def test_rejects_wrong_chain():
    settings = Settings(chains=("base",))
    verdict = evaluate(_pair(chain="ethereum"), settings)
    assert verdict.accepted is False


def test_solana_quote_not_rejected_as_chain():
    settings = Settings(chains=("solana",), min_age_min=0, max_age_hours=100000)
    verdict = evaluate(_pair(chain="solana", quote_symbol="SOL"), settings)
    assert not any(r.startswith("chain=") or r.startswith("quote=") for r in verdict.reasons)
