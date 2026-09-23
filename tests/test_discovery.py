from desk_radar.discovery import quality_score
from desk_radar.models import PairSnapshot


def test_higher_volume_scores_higher():
    low = PairSnapshot(
        chain="base",
        pair_address="a",
        base_address="a",
        base_symbol="A",
        quote_symbol="WETH",
        price_usd=1,
        liquidity_usd=20_000,
        volume_5m_usd=1_000,
        pair_created_at_ms=1_700_000_000_000,
    )
    high = PairSnapshot(
        chain="base",
        pair_address="b",
        base_address="b",
        base_symbol="B",
        quote_symbol="WETH",
        price_usd=1,
        liquidity_usd=20_000,
        volume_5m_usd=20_000,
        pair_created_at_ms=1_700_000_000_000,
    )
    assert quality_score(high) > quality_score(low)
