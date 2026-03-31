# TrustWise Quick Start (Web)

## Prerequisites

- Complete Python setup first (`pip install -r requirements.txt`).
- Node.js 18+.

## Start Web App

```bash
cd web
npm install
npm run build
npm start
```

Open `http://127.0.0.1:5000`.

## Optional Launch Scripts

- Windows: `scripts/start_web.bat`
- Linux/macOS: `scripts/start_web.sh`

## API Smoke Checks

```bash
curl http://127.0.0.1:5000/api/status
curl http://127.0.0.1:5000/api/plans
```

Bridge smoke:

```bash
echo '{"action":"status"}' | python api_bridge.py
```

## Notes

- The Express server delegates execution to `api_bridge.py`.
- Set `PYTHON_EXE` or `TRUSTWISE_PYTHON` when PATH points to the wrong Python interpreter.
- If provider endpoints are unavailable, the system still runs in mock planning mode.

For endpoint details see [FRONTEND.md](FRONTEND.md).

