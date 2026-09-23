from datetime import datetime, timedelta, timezone

from desk_radar.config import Settings
from desk_radar.engine import run_cycle
from desk_radar.models import PairSnapshot
from desk_radar.rug import RugVerdict


class FakeDiscovery:
    def __init__(self, pairs: list[PairSnapshot]) -> None:
        self.pairs = pairs

    def harvest(self) -> list[PairSnapshot]:
        return list(self.pairs)

    def refresh(self, address: str) -> list[PairSnapshot]:
        return [p for p in self.pairs if p.base_address == address]


class FakeRug:
    def __init__(self, accept: bool = True) -> None:
        self.accept = accept

    def check(self, pair: PairSnapshot) -> RugVerdict:
        return RugVerdict(
            pair=pair, accepted=self.accept, reasons=[] if self.accept else ["honeypot"]
        )


def _fresh_pair() -> PairSnapshot:
    created = datetime.now(timezone.utc) - timedelta(minutes=30)
    return PairSnapshot(
        chain="base",
        pair_address="0xpair",
        base_address="0xbase",
        base_symbol="TEST",
        quote_symbol="WETH",
        price_usd=0.01,
        liquidity_usd=80_000,
        volume_5m_usd=12_000,
        pair_created_at_ms=int(created.timestamp() * 1000),
    )


def test_cycle_opens_paper_when_filters_and_rug_pass(tmp_path):
    pair = _fresh_pair()
    settings = Settings(state_dir=str(tmp_path), chains=("base",))
    result = run_cycle(settings, discovery=FakeDiscovery([pair]), rug=FakeRug(True))
    assert result.scanned == 1
    assert len(result.accepted) == 1
    assert len(result.opened) == 1
    assert result.opened[0].base_symbol == "TEST"


def test_cycle_blocks_rugged_token(tmp_path):
    pair = _fresh_pair()
    settings = Settings(state_dir=str(tmp_path), chains=("base",))
    result = run_cycle(settings, discovery=FakeDiscovery([pair]), rug=FakeRug(False))
    assert result.opened == []
    assert len(result.rugged) == 1
