# Desk Radar

Paper-first meme radar for **Base** and **Solana**.

No Webull. No Kraken. No wallet. No live swap.

```
PAPER_TRADING=true
DRY_RUN=true
ALLOW_LIVE_TRADING=false
```

Official $MAYO watch address (Base, no pool yet):

`0x1775A38Cd04f1Da9Ec35D205491fE71DeA90aFF9`

Dublin- stays the Kraken/BTC desk. This repo is the on-chain discovery lane.

## Pipeline

```
locks → discovery → market filters → rug gate → paper book → TP/SL mark
```

Discovery pulls DexScreener search + token profiles, keeps allowed quotes only
(WETH/USDC/USDT on Base, SOL/USDC/USDT on Solana), ranks by volume × log(liq) / age.

Rug gate asks GoPlus and fail-closes on outage. Blocked tokens go to `.state/rejects.json`.

Paper budget defaults to $25, max 3 open, +25% / −18%.

## Setup

```bash
cd desk-radar
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
PYTHONPATH=src python -m desk_radar doctor
PYTHONPATH=src python -m pytest -q
```

No third-party packages are required to run or test.

## Commands

```bash
python -m desk_radar doctor
python -m desk_radar scan-once
python -m desk_radar book
python -m desk_radar rejects
python -m desk_radar watch-mayo
python -m desk_radar watch-vink
```

## Docs

- [SAFETY.md](SAFETY.md) — locks and residual risk
- [RUNBOOK.md](RUNBOOK.md) — daily ops
- [PHASES.md](PHASES.md) — what shipped

This software does not guarantee profit. Paper fills are simulated.
