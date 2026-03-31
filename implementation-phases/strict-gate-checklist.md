# Strict Phase Gate Checklist

Use this checklist at each phase boundary before moving forward.

## Required gate signals

1. Phase scope tasks were implemented (code/docs/config as applicable).
2. Phase evidence was recorded in `implementation-phases/execution-evidence.md`.
3. No new linter diagnostics in touched files.
4. Applicable runtime checks pass:
   - `python test_basic.py` (with UTF-8 console env when needed)
   - `python test_comprehensive.py` (with UTF-8 console env when needed)
   - `cd web && npm run build`
   - `echo '{"action":"status"}' | python api_bridge.py`

## Windows console encoding note

If Unicode output fails in cp1252 consoles, run Python checks with:

```powershell
$env:PYTHONIOENCODING='utf-8'
python test_basic.py
python test_comprehensive.py
```

## Gate decision

- Pass: continue to next phase.
- Fail: stop progression, fix issue, rerun checks, then proceed.

