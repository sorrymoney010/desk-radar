from __future__ import annotations

import argparse
import sys

from desk_radar.book import PaperBook
from desk_radar.config import settings
from desk_radar.dexscreener import DexScreener
from desk_radar.engine import run_cycle
from desk_radar.ledger import RejectLedger
from desk_radar.safety import assert_locks, live_execution_blocked


def cmd_doctor(_: argparse.Namespace) -> int:
    assert_locks(settings)
    print("desk-radar doctor")
    print(
        f"  locks        paper={settings.paper_trading} "
        f"dry_run={settings.dry_run} live={settings.allow_live_trading}"
    )
    print(f"  execution    {live_execution_blocked()}")
    print(f"  chains       {','.join(settings.chains)}")
    print(f"  min_liq      {settings.min_liq_usd}")
    print(f"  min_vol_5m   {settings.min_vol_5m}")
    print(f"  paper_budget {settings.paper_budget_usd}")
    print(f"  rug          fail_closed={settings.rug_fail_closed}")
    print(f"  mayo_ca      {settings.mayo_ca}")
    print(f"  vink_ca      {settings.vink_ca or '(unset)'}")
    return 0


def cmd_scan_once(_: argparse.Namespace) -> int:
    result = run_cycle(settings)
    print(
        f"scanned={result.scanned} accepted={len(result.accepted)} "
        f"rugged={len(result.rugged)} opened={len(result.opened)} "
        f"closed={len(result.closed)}"
    )
    for pos in result.opened:
        print(
            f"  PAPER BUY  {pos.base_symbol} {pos.base_address[:10]}... "
            f"@ {pos.entry_price} size=${pos.size_usd}"
        )
    for pos in result.closed:
        print(f"  PAPER SELL {pos.base_symbol} @ {pos.exit_price} {pos.exit_reason}")
    for verdict in result.rugged[:8]:
        print(
            f"  RUG BLOCK  {verdict.pair.base_symbol} "
            f"{','.join(verdict.reasons) or 'unknown'}"
        )
    if not result.opened:
        print("  no new paper entries (filters, rug gate, or book full)")
    return 0


def cmd_book(_: argparse.Namespace) -> int:
    assert_locks(settings)
    ledger = PaperBook(settings)
    print(f"open={len(ledger.open_positions())} total={len(ledger.positions)}")
    for pos in ledger.positions[-20:]:
        extra = f" exit={pos.exit_price} {pos.exit_reason}" if pos.status == "closed" else ""
        print(f"  {pos.status:6} {pos.base_symbol:10} entry={pos.entry_price}{extra}")
    return 0


def cmd_rejects(_: argparse.Namespace) -> int:
    assert_locks(settings)
    ledger = RejectLedger(settings)
    print(f"rejects={len(ledger.rows)}")
    for row in ledger.rows[-20:]:
        print(f"  {row.get('symbol')} {row.get('address')} {row.get('reasons')}")
    return 0


def _watch_token(label: str, address: str, chain: str) -> int:
    assert_locks(settings)
    if not address:
        print(f"{label} CA unset")
        return 0
    print(f"{label} {address}")
    dex = DexScreener(settings)
    try:
        pairs = [p for p in dex.token_pairs(address) if p.chain.lower() == chain]
    except RuntimeError as exc:
        print(f"  lookup failed ({exc})")
        return 0
    if not pairs:
        print(f"  no {chain} pair on DexScreener yet - token may exist without a pool")
        return 0
    for p in pairs:
        print(
            f"  {p.base_symbol}/{p.quote_symbol} liq=${p.liquidity_usd:.0f} "
            f"px={p.price_usd} {p.url}"
        )
    return 0


def cmd_watch_mayo(_: argparse.Namespace) -> int:
    return _watch_token("$MAYO", settings.mayo_ca, "base")


def cmd_watch_vink(_: argparse.Namespace) -> int:
    return _watch_token("$VINK", settings.vink_ca, "solana")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="desk-radar")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    sub.add_parser("scan-once").set_defaults(func=cmd_scan_once)
    sub.add_parser("book").set_defaults(func=cmd_book)
    sub.add_parser("rejects").set_defaults(func=cmd_rejects)
    sub.add_parser("watch-mayo").set_defaults(func=cmd_watch_mayo)
    sub.add_parser("watch-vink").set_defaults(func=cmd_watch_vink)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
