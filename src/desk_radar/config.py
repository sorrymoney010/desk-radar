from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    return default if raw is None else float(raw)


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    return default if raw is None else int(raw)


def _csv(name: str, default: str) -> tuple[str, ...]:
    raw = os.environ.get(name, default)
    return tuple(part.strip().lower() for part in raw.split(",") if part.strip())


@dataclass(frozen=True)
class Settings:
    paper_trading: bool = True
    dry_run: bool = True
    allow_live_trading: bool = False
    chains: tuple[str, ...] = ("base", "solana")
    min_liq_usd: float = 15_000
    min_vol_5m: float = 3_000
    min_age_min: float = 2
    max_age_hours: float = 36
    paper_budget_usd: float = 25
    max_open_positions: int = 3
    take_profit_pct: float = 25
    stop_loss_pct: float = 18
    max_candidates: int = 25
    max_buy_tax_pct: float = 5
    max_sell_tax_pct: float = 5
    rug_fail_closed: bool = True
    mayo_ca: str = "0x1775A38Cd04f1Da9Ec35D205491fE71DeA90aFF9"
    vink_ca: str = ""
    state_dir: str = ".state"
    dexscreener_base: str = "https://api.dexscreener.com"
    goplus_base: str = "https://api.gopluslabs.io"

    def locks_engaged(self) -> bool:
        return self.paper_trading and self.dry_run and not self.allow_live_trading

    @property
    def chain(self) -> str:
        return self.chains[0] if self.chains else "base"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            paper_trading=_bool("PAPER_TRADING", True),
            dry_run=_bool("DRY_RUN", True),
            allow_live_trading=_bool("ALLOW_LIVE_TRADING", False),
            chains=_csv("CHAINS", "base,solana"),
            min_liq_usd=_float("MIN_LIQ_USD", 15_000),
            min_vol_5m=_float("MIN_VOL_5M", 3_000),
            min_age_min=_float("MIN_AGE_MIN", 2),
            max_age_hours=_float("MAX_AGE_HOURS", 36),
            paper_budget_usd=_float("PAPER_BUDGET_USD", 25),
            max_open_positions=_int("MAX_OPEN_POSITIONS", 3),
            take_profit_pct=_float("TAKE_PROFIT_PCT", 25),
            stop_loss_pct=_float("STOP_LOSS_PCT", 18),
            max_candidates=_int("MAX_CANDIDATES", 25),
            max_buy_tax_pct=_float("MAX_BUY_TAX_PCT", 5),
            max_sell_tax_pct=_float("MAX_SELL_TAX_PCT", 5),
            rug_fail_closed=_bool("RUG_FAIL_CLOSED", True),
            mayo_ca=os.environ.get("MAYO_CA", "0x1775A38Cd04f1Da9Ec35D205491fE71DeA90aFF9"),
            vink_ca=os.environ.get("VINK_CA", ""),
            state_dir=os.environ.get("STATE_DIR", ".state"),
            dexscreener_base=os.environ.get("DEXSCREENER_BASE", "https://api.dexscreener.com"),
            goplus_base=os.environ.get("GOPLUS_BASE", "https://api.gopluslabs.io"),
        )


settings = Settings.from_env()
