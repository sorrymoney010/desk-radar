from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class PairSnapshot:
    chain: str
    pair_address: str
    base_address: str
    base_symbol: str
    quote_symbol: str
    price_usd: float
    liquidity_usd: float
    volume_5m_usd: float
    pair_created_at_ms: int | None = None
    url: str = ""

    @property
    def age_minutes(self) -> float | None:
        if not self.pair_created_at_ms:
            return None
        created = datetime.fromtimestamp(self.pair_created_at_ms / 1000, tz=timezone.utc)
        return (utcnow() - created).total_seconds() / 60


@dataclass
class FilterVerdict:
    pair: PairSnapshot
    accepted: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class PaperFill:
    side: Literal["buy", "sell"]
    usd: float
    price: float
    at: datetime = field(default_factory=utcnow)


@dataclass
class PaperPosition:
    pair_address: str
    base_address: str
    base_symbol: str
    entry_price: float
    size_usd: float
    opened_at: datetime = field(default_factory=utcnow)
    status: Literal["open", "closed"] = "open"
    exit_price: float | None = None
    exit_reason: str | None = None
    fills: list[PaperFill] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "pair_address": self.pair_address,
            "base_address": self.base_address,
            "base_symbol": self.base_symbol,
            "entry_price": self.entry_price,
            "size_usd": self.size_usd,
            "opened_at": self.opened_at.isoformat(),
            "status": self.status,
            "exit_price": self.exit_price,
            "exit_reason": self.exit_reason,
            "fills": [
                {
                    "side": f.side,
                    "usd": f.usd,
                    "price": f.price,
                    "at": f.at.isoformat(),
                }
                for f in self.fills
            ],
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "PaperPosition":
        fills = [
            PaperFill(
                side=row["side"],
                usd=row["usd"],
                price=row["price"],
                at=datetime.fromisoformat(row["at"]),
            )
            for row in raw.get("fills") or []
        ]
        return cls(
            pair_address=raw["pair_address"],
            base_address=raw["base_address"],
            base_symbol=raw["base_symbol"],
            entry_price=raw["entry_price"],
            size_usd=raw["size_usd"],
            opened_at=datetime.fromisoformat(raw["opened_at"]),
            status=raw.get("status", "open"),
            exit_price=raw.get("exit_price"),
            exit_reason=raw.get("exit_reason"),
            fills=fills,
        )
