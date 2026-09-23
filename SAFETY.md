# SAFETY

Desk Radar cannot place a live swap. That is intentional.

## Locks

| Flag | Required value |
|---|---|
| `PAPER_TRADING` | `true` |
| `DRY_RUN` | `true` |
| `ALLOW_LIVE_TRADING` | `false` |

`desk-radar doctor` and every trading command call `assert_locks()`. If live is on, the process exits before discovery runs.

There is no wallet module. There is no signer. There is no Uniswap / Jupiter / Pump.fun execution path in this version.

## Residual risks

1. Paper fills are not live fills. DexScreener prices lag and ignore slippage.
2. GoPlus is a third-party snapshot. A clean verdict is not a guarantee.
3. If `RUG_FAIL_CLOSED=true` (default) and GoPlus is down, candidates are skipped. That is safer than trading blind.
4. Discovery search is noisy. Ranking reduces junk; it does not remove it.
5. $MAYO has no pool yet. Watching the CA does not create liquidity.
6. Cheap price is not an edge.

## Pre-live checklist (not enabled)

Do not flip live flags in this repo. A live sleeve would need its own review:

- dedicated hot wallet with a hard cap
- no withdrawal keys on the box
- signed-tx dry run against a fork
- explicit per-chain router allowlist
- separate SAFETY review, same bar as Dublin-
