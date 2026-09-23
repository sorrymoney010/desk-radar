from __future__ import annotations

from desk_radar.config import Settings


class SafetyError(RuntimeError):
    pass


def assert_locks(settings: Settings) -> None:
    if settings.allow_live_trading:
        raise SafetyError("ALLOW_LIVE_TRADING is true — desk-radar refuses to start.")
    if not settings.paper_trading or not settings.dry_run:
        raise SafetyError("Paper / dry-run locks are off — desk-radar refuses to start.")


def live_execution_blocked() -> str:
    return "live execution is hard-blocked; paper book only"
