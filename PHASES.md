# Phases

Status as of 2026-09-23. All build phases below are in tree. Push/commit happens after tests pass.

## P0 — Paper core — done

Locks, DexScreener parse, market filters, paper book, `doctor` / `scan-once` / `book`.

## P1 — Tighter discovery — done

Multi-query harvest per chain, token-profile ingest, pair dedupe, quality ranking, candidate cap.

## P2 — Rug gate — done

GoPlus EVM + Solana security snapshot. Honeypot / mint / freeze / tax hard fails. Fail-closed on outage. Reject ledger.

## P3 — Solana sleeve — done

`CHAINS=base,solana`. SOL/USDC quotes. Solana rug keys. `$VINK` watch command (CA optional via `VINK_CA`).

## P4 — Ops — done

SAFETY.md, RUNBOOK.md, CI workflow, offline unit tests.

## Out of scope (not a phase in this repo)

Live swaps, private keys, Pump.fun sniping, Webull, Kraken.
