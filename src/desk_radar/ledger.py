from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from desk_radar.config import Settings


class RejectLedger:
    def __init__(self, settings: Settings) -> None:
        self.path = Path(settings.state_dir) / "rejects.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rows: list[dict] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        self.rows = json.loads(self.path.read_text())

    def save(self) -> None:
        self.path.write_text(json.dumps(self.rows[-500:], indent=2))

    def known(self, address: str) -> bool:
        needle = address.lower()
        return any(row.get("address", "").lower() == needle for row in self.rows)

    def add(self, address: str, symbol: str, reasons: list[str]) -> None:
        if self.known(address):
            return
        self.rows.append(
            {
                "address": address,
                "symbol": symbol,
                "reasons": reasons,
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.save()
