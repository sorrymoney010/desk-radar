from __future__ import annotations

import json
from pathlib import Path

from desk_radar.config import Settings
from desk_radar.models import PaperFill, PaperPosition, PairSnapshot


class PaperBook:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.path = Path(settings.state_dir) / "paper_book.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.positions: list[PaperPosition] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        raw = json.loads(self.path.read_text())
        self.positions = [PaperPosition.from_dict(row) for row in raw]

    def save(self) -> None:
        self.path.write_text(json.dumps([p.to_dict() for p in self.positions], indent=2))

    def open_positions(self) -> list[PaperPosition]:
        return [p for p in self.positions if p.status == "open"]

    def has_open(self, pair_address: str) -> bool:
        needle = pair_address.lower()
        return any(p.pair_address.lower() == needle and p.status == "open" for p in self.positions)

    def open_paper(self, pair: PairSnapshot) -> PaperPosition | None:
        if len(self.open_positions()) >= self.settings.max_open_positions:
            return None
        if self.has_open(pair.pair_address):
            return None
        pos = PaperPosition(
            pair_address=pair.pair_address,
            base_address=pair.base_address,
            base_symbol=pair.base_symbol,
            entry_price=pair.price_usd,
            size_usd=self.settings.paper_budget_usd,
            fills=[PaperFill(side="buy", usd=self.settings.paper_budget_usd, price=pair.price_usd)],
        )
        self.positions.append(pos)
        self.save()
        return pos

    def mark(self, pair: PairSnapshot) -> PaperPosition | None:
        needle = pair.pair_address.lower()
        pos = next((p for p in self.open_positions() if p.pair_address.lower() == needle), None)
        if pos is None or pair.price_usd <= 0:
            return None
        change = (pair.price_usd - pos.entry_price) / pos.entry_price * 100
        reason = None
        if change >= self.settings.take_profit_pct:
            reason = f"tp:{change:.1f}%"
        elif change <= -self.settings.stop_loss_pct:
            reason = f"sl:{change:.1f}%"
        if reason is None:
            return pos
        pos.status = "closed"
        pos.exit_price = pair.price_usd
        pos.exit_reason = reason
        pos.fills.append(
            PaperFill(side="sell", usd=pos.size_usd * (1 + change / 100), price=pair.price_usd)
        )
        self.save()
        return pos
