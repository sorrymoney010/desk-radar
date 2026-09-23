from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from desk_radar.config import Settings
from desk_radar.http import get_json
from desk_radar.models import PairSnapshot

CHAIN_ID = {"ethereum": "1", "eth": "1", "base": "8453", "bsc": "56"}

EVM_HARD_FAILS = (
    "is_honeypot",
    "cannot_sell_all",
    "is_blacklisted",
    "hidden_owner",
    "can_take_back_ownership",
    "is_mintable",
    "trading_cooldown",
    "transfer_pausable",
)

SOL_HARD_FAILS = (
    "is_honeypot",
    "mintable",
    "freezable",
    "balance_mutable_authority",
    "closable",
    "default_account_state_frozen",
    "transfer_fee_upgradable",
    "transfer_hook_upgradable",
)


@dataclass
class RugVerdict:
    pair: PairSnapshot
    accepted: bool
    reasons: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


def _flag_on(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _pct(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


class RugGate:
    def __init__(self, settings: Settings, fetcher: Callable[[str], Any] | None = None) -> None:
        self.settings = settings
        self._fetcher = fetcher or get_json

    def check(self, pair: PairSnapshot) -> RugVerdict:
        chain = pair.chain.lower()
        try:
            raw = self._fetch(chain, pair.base_address)
        except RuntimeError as exc:
            if self.settings.rug_fail_closed:
                return RugVerdict(pair=pair, accepted=False, reasons=[f"rug_unavailable:{exc}"])
            return RugVerdict(pair=pair, accepted=True, reasons=["rug_skipped"])
        if not raw:
            if self.settings.rug_fail_closed:
                return RugVerdict(pair=pair, accepted=False, reasons=["rug_empty"])
            return RugVerdict(pair=pair, accepted=True, reasons=["rug_empty_open"])
        if chain == "solana":
            return self._solana(pair, raw)
        return self._evm(pair, raw)

    def _fetch(self, chain: str, address: str) -> dict[str, Any]:
        if chain == "solana":
            url = f"{self.settings.goplus_base}/api/v1/solana/token_security?contract_addresses={address}"
        else:
            cid = CHAIN_ID.get(chain)
            if cid is None:
                raise RuntimeError(f"unsupported_chain:{chain}")
            url = f"{self.settings.goplus_base}/api/v1/token_security/{cid}?contract_addresses={address}"
        payload = self._fetcher(url)
        result = payload.get("result") if isinstance(payload, dict) else None
        if isinstance(result, dict):
            if address.lower() in {k.lower() for k in result}:
                for key, value in result.items():
                    if key.lower() == address.lower() and isinstance(value, dict):
                        return value
            if len(result) == 1:
                only = next(iter(result.values()))
                if isinstance(only, dict):
                    return only
        return result if isinstance(result, dict) else {}

    def _evm(self, pair: PairSnapshot, raw: dict[str, Any]) -> RugVerdict:
        reasons: list[str] = []
        for key in EVM_HARD_FAILS:
            if _flag_on(raw.get(key)):
                reasons.append(key)
        buy_tax = _pct(raw.get("buy_tax"))
        sell_tax = _pct(raw.get("sell_tax"))
        if buy_tax > self.settings.max_buy_tax_pct:
            reasons.append(f"buy_tax={buy_tax}")
        if sell_tax > self.settings.max_sell_tax_pct:
            reasons.append(f"sell_tax={sell_tax}")
        return RugVerdict(pair=pair, accepted=not reasons, reasons=reasons, raw=raw)

    def _solana(self, pair: PairSnapshot, raw: dict[str, Any]) -> RugVerdict:
        reasons: list[str] = []
        for key in SOL_HARD_FAILS:
            if _flag_on(raw.get(key)):
                reasons.append(key)
        return RugVerdict(pair=pair, accepted=not reasons, reasons=reasons, raw=raw)
