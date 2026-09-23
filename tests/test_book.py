from desk_radar.book import PaperBook
from desk_radar.config import Settings
from desk_radar.models import PairSnapshot


def _pair(price: float = 1.0) -> PairSnapshot:
    return PairSnapshot(
        chain="base",
        pair_address="0xpair",
        base_address="0xbase",
        base_symbol="TEST",
        quote_symbol="WETH",
        price_usd=price,
        liquidity_usd=50_000,
        volume_5m_usd=10_000,
        pair_created_at_ms=1_700_000_000_000,
    )


def test_open_and_take_profit(tmp_path):
    settings = Settings(state_dir=str(tmp_path), take_profit_pct=20, stop_loss_pct=50, paper_budget_usd=25)
    book = PaperBook(settings)
    opened = book.open_paper(_pair(1.0))
    assert opened is not None
    assert opened.status == "open"
    closed = book.mark(_pair(1.25))
    assert closed is not None
    assert closed.status == "closed"
    assert closed.exit_reason and closed.exit_reason.startswith("tp:")
