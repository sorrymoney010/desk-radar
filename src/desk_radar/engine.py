from __future__ import annotations

from desk_radar.book import PaperBook
from desk_radar.config import Settings
from desk_radar.discovery import Discovery
from desk_radar.filters import evaluate
from desk_radar.ledger import RejectLedger
from desk_radar.models import FilterVerdict, PaperPosition, PairSnapshot
from desk_radar.rug import RugGate, RugVerdict
from desk_radar.safety import assert_locks


class CycleResult:
    def __init__(self) -> None:
        self.scanned: int = 0
        self.accepted: list[FilterVerdict] = []
        self.rejected: list[FilterVerdict] = []
        self.rugged: list[RugVerdict] = []
        self.opened: list[PaperPosition] = []
        self.closed: list[PaperPosition] = []


def _mark_open(
    book: PaperBook,
    discovery: Discovery,
    harvested: list[PairSnapshot],
    result: CycleResult,
) -> None:
    by_pair = {s.pair_address.lower(): s for s in harvested}
    for pos in list(book.open_positions()):
        snap = by_pair.get(pos.pair_address.lower())
        if snap is None:
            refreshed = discovery.refresh(pos.base_address)
            snap = next(
                (s for s in refreshed if s.pair_address.lower() == pos.pair_address.lower()),
                refreshed[0] if refreshed else None,
            )
        if snap is None:
            continue
        marked = book.mark(snap)
        if marked and marked.status == "closed":
            result.closed.append(marked)


def run_cycle(
    settings: Settings,
    discovery: Discovery | None = None,
    rug: RugGate | None = None,
) -> CycleResult:
    assert_locks(settings)
    discovery = discovery or Discovery(settings)
    rug = rug or RugGate(settings)
    book = PaperBook(settings)
    rejects = RejectLedger(settings)
    result = CycleResult()

    harvested = discovery.harvest()
    result.scanned = len(harvested)
    _mark_open(book, discovery, harvested, result)

    for snap in harvested:
        if rejects.known(snap.base_address):
            result.rejected.append(
                FilterVerdict(pair=snap, accepted=False, reasons=["reject_ledger"])
            )
            continue
        market = evaluate(snap, settings)
        if not market.accepted:
            result.rejected.append(market)
            continue
        security = rug.check(snap)
        if not security.accepted:
            result.rugged.append(security)
            rejects.add(snap.base_address, snap.base_symbol, security.reasons)
            continue
        result.accepted.append(market)
        opened = book.open_paper(snap)
        if opened:
            result.opened.append(opened)

    return result
