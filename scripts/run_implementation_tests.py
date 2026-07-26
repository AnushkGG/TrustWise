#!/usr/bin/env python3
"""
Automate the manual checklist in implementationtest.md (Phases 1, 2, 4; optional HTTP).

Run from repository root:
    python scripts/run_implementation_tests.py

Options:
    --ci          CI mode: same as default but skips HTTP (no server on runners).
    --no-npm      Skip npm ci / npm run build (Phase 1 web build).
    --no-config   Skip Phase 2 (Config.validate).
    --no-bridge   Skip Phase 4a (api_bridge status).
    --http        Try GET /api/status on http://127.0.0.1:5000 (Phase 4b). Default on.
    --no-http     Do not try HTTP.
    --strict-http Fail if HTTP check cannot connect (default: skip if server down).

Exit code 0 if all executed phases pass.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _chdir_root() -> None:
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def phase1_python() -> None:
    print("\n=== Phase 1a: Python tests ===")
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    for script in ("test_basic.py", "test_comprehensive.py"):
        subprocess.run([sys.executable, script], cwd=ROOT, env=env, check=True)
    print("[PASS] test_basic.py + test_comprehensive.py")


def phase1_npm() -> None:
    print("\n=== Phase 1b: Web npm ci + build ===")
    web = ROOT / "frontend"
    kwargs: dict = {"cwd": web, "check": True}
    
    has_build = False
    pkg_json_path = web / "package.json"
    if pkg_json_path.exists():
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
                has_build = "build" in pkg.get("scripts", {})
        except Exception:
            pass

    if sys.platform == "win32":
        subprocess.run("npm ci", shell=True, **kwargs)
        if has_build:
            subprocess.run("npm run build", shell=True, **kwargs)
    else:
        subprocess.run(["npm", "ci"], **kwargs)
        if has_build:
            subprocess.run(["npm", "run", "build"], **kwargs)
    print("[PASS] web build")


def phase2_config() -> None:
    print("\n=== Phase 2: Config.validate() ===")
    _chdir_root()
    if not (ROOT / ".env").exists():
        print("[SKIP] No .env file — copy .env.example to .env for full Phase 2.")
        return
    from utils.config import Config

    try:
        Config.validate()
    except ValueError as e:
        print(f"[FAIL] Config.validate(): {e}")
        raise SystemExit(1) from e
    print("[PASS] Config.validate()")


def phase4_bridge() -> None:
    print("\n=== Phase 4a: api_bridge status (stdin JSON) ===")
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    proc = subprocess.run(
        [sys.executable, "api_bridge.py"],
        cwd=ROOT,
        env=env,
        input='{"action":"status"}\n',
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        print(proc.stderr)
        raise SystemExit(f"api_bridge exited {proc.returncode}")
    line = proc.stdout.strip()
    if not line:
        raise SystemExit("api_bridge produced empty stdout")
    data = json.loads(line)
    if not data.get("success"):
        raise SystemExit(f"api_bridge status not success: {data}")
    st = data.get("status") or {}
    for key in ("llm_provider", "llm_model", "has_api_key"):
        if key not in st:
            raise SystemExit(f"status missing key: {key}")
    print("[PASS] api_bridge status JSON OK")
    print(f"      llm_provider={st.get('llm_provider')} has_api_key={st.get('has_api_key')}")


def phase4_http(strict: bool) -> None:
    print("\n=== Phase 4b: HTTP GET /api/status (optional) ===")
    try:
        import requests
    except ImportError:
        print("[SKIP] requests not installed")
        return
    url = os.environ.get("TRUSTWISE_STATUS_URL", "http://127.0.0.1:5000/api/status")
    try:
        r = requests.get(url, timeout=2)
    except requests.RequestException as e:
        msg = f"[SKIP] No server at {url} ({e})"
        if strict:
            raise SystemExit(msg.replace("[SKIP]", "[FAIL]")) from e
        print(msg)
        return
    if r.status_code != 200:
        raise SystemExit(f"HTTP {r.status_code} from {url}")
    body = r.json()
    if not body.get("success"):
        raise SystemExit(f"API success=false: {body}")
    print(f"[PASS] {url} returned success")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run implementation test plan automation")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: skip HTTP check (no Express server on runner)",
    )
    parser.add_argument("--no-npm", action="store_true", help="Skip npm ci / build")
    parser.add_argument("--no-config", action="store_true", help="Skip Config.validate")
    parser.add_argument("--no-bridge", action="store_true", help="Skip api_bridge smoke")
    parser.add_argument("--http", dest="http", action="store_true", default=True, help="Try HTTP (default)")
    parser.add_argument("--no-http", dest="http", action="store_false", help="Skip HTTP check")
    parser.add_argument(
        "--strict-http",
        action="store_true",
        help="Fail if HTTP check cannot reach the server",
    )
    args = parser.parse_args()

    _chdir_root()
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    print("TrustWise — automated implementation checks", flush=True)
    print(f"ROOT={ROOT}", flush=True)

    phase1_python()
    if not args.no_npm:
        phase1_npm()
    else:
        print("\n=== Phase 1b: SKIPPED (--no-npm) ===")

    if not args.no_config:
        phase2_config()
    else:
        print("\n=== Phase 2: SKIPPED (--no-config) ===")

    if not args.no_bridge:
        phase4_bridge()
    else:
        print("\n=== Phase 4a: SKIPPED (--no-bridge) ===")

    do_http = args.http and not args.ci
    if do_http:
        phase4_http(strict=args.strict_http)
    else:
        print("\n=== Phase 4b: SKIPPED (no HTTP: --ci or --no-http) ===")

    print("\n=== Done: all automated phases passed ===")
    print("Manual only: Phase 3 (live Ollama/Gemini/both), Phase 5 (browser UX), Phase 6 (deploy docs).")


if __name__ == "__main__":
    main()
