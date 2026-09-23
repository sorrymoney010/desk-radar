# RUNBOOK

## Daily

```bash
PYTHONPATH=src python -m desk_radar doctor
PYTHONPATH=src python -m desk_radar scan-once
PYTHONPATH=src python -m desk_radar book
PYTHONPATH=src python -m desk_radar rejects
PYTHONPATH=src python -m desk_radar watch-mayo
PYTHONPATH=src python -m desk_radar watch-vink
```

State files live under `STATE_DIR` (default `.state/`):

- `paper_book.json` — paper positions
- `rejects.json` — tokens the rug gate blocked

## Incidents

| Symptom | Action |
|---|---|
| doctor fails on locks | Do not “fix” by enabling live. Restore `.env` from `.env.example`. |
| scan-once returns scanned=0 | DexScreener blocked or network down. Retry later. Paper book is unchanged. |
| everything rugged | GoPlus outage with fail-closed on. Wait. Do not set `RUG_FAIL_CLOSED=false` to force entries. |
| book full | Close via TP/SL on the next scan, or raise `MAX_OPEN_POSITIONS` only after reviewing open risk. |

## What not to do

- Do not paste a private key into this repo.
- Do not point this process at a live router.
- Do not treat paper PnL as live edge.
