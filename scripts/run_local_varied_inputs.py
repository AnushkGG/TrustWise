#!/usr/bin/env python3
"""
Run TrustWise locally with varied HTTP/bridge inputs; save raw logs + summary under
logs/local-test/run-<timestamp>/.

Usage (repo root):
    python scripts/run_local_varied_inputs.py
"""
from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
HOST = os.environ.get("TRUSTWISE_HOST", "127.0.0.1")


def _pick_port() -> int:
    if os.environ.get("PORT"):
        return int(os.environ["PORT"])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, 0))
        return int(s.getsockname()[1])


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")


def _run(cmd: list[str], cwd: Path, log: Path, env: dict | None = None) -> tuple[int, str]:
    e = os.environ.copy()
    e.setdefault("PYTHONIOENCODING", "utf-8")
    if env:
        e.update(env)
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, timeout=600)
    out = f"=== CMD ===\n{' '.join(cmd)}\n=== CWD ===\n{cwd}\n=== EXIT ===\n{p.returncode}\n\n=== STDOUT ===\n{p.stdout}\n\n=== STDERR ===\n{p.stderr}\n"
    _write(log, out)
    return p.returncode, out


def _wait_port(port: int, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s = socket.create_connection((HOST, port), timeout=1)
            s.close()
            return True
        except OSError:
            time.sleep(0.3)
    return False


def _bridge(stdin_line: str, log: Path) -> tuple[int, str, str]:
    p = subprocess.run(
        [sys.executable, str(ROOT / "api_bridge.py")],
        cwd=ROOT,
        input=stdin_line + "\n",
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=120,
    )
    _write(log, f"stdin={stdin_line!r}\nexit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}\n")
    return p.returncode, p.stdout, p.stderr


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    log_dir = ROOT / "logs" / "local-test" / f"run-{ts}"
    log_dir.mkdir(parents=True, exist_ok=True)

    issues: list[tuple[str, str]] = []
    matrix: list[tuple[str, str, str]] = []

    # --- Phase: Python unit tests ---
    for name, script in [("test_basic", "test_basic.py"), ("test_comprehensive", "test_comprehensive.py")]:
        rc, _ = _run([sys.executable, script], ROOT, log_dir / f"phase-{name}.log")
        matrix.append(("Phase 1", name, "PASS" if rc == 0 else "FAIL"))
        if rc != 0:
            issues.append((name, f"exit code {rc}"))

    # --- Phase: npm (shell on Windows so npm.cmd resolves) ---
    def _npm(step: str, log_name: str) -> int:
        e = os.environ.copy()
        e.setdefault("PYTHONIOENCODING", "utf-8")
        if sys.platform == "win32":
            p = subprocess.run(
                step,
                shell=True,
                cwd=WEB,
                env=e,
                capture_output=True,
                text=True,
                timeout=600,
            )
        else:
            p = subprocess.run(
                step.split(),
                cwd=WEB,
                env=e,
                capture_output=True,
                text=True,
                timeout=600,
            )
        _write(
            log_dir / log_name,
            f"=== CMD ===\n{step}\n=== EXIT ===\n{p.returncode}\n\n{p.stdout}\n\n{p.stderr}\n",
        )
        return p.returncode

    rc_ci = _npm("npm ci", "phase-npm-ci.log")
    rc_bd = _npm("npm run build", "phase-npm-build.log")
    matrix.append(("Phase 1", "npm ci", "PASS" if rc_ci == 0 else "FAIL"))
    matrix.append(("Phase 1", "npm run build", "PASS" if rc_bd == 0 else "FAIL"))
    if rc_ci != 0:
        issues.append(("npm ci", f"exit {rc_ci}"))
    if rc_bd != 0:
        issues.append(("npm build", f"exit {rc_bd}"))

    # --- Bridge: varied stdin ---
    bridge_cases = [
        ("bridge-status", '{"action":"status"}'),
        ("bridge-empty", "{}"),
        ("bridge-unknown-action", '{"action":"not_a_real_action"}'),
    ]
    for label, payload in bridge_cases:
        rc, out, err = _bridge(payload, log_dir / f"bridge-{label}.log")
        ok = rc == 0 and out.strip()
        matrix.append(("Bridge", label, "PASS" if ok else "FAIL/NONE"))
        if not ok:
            issues.append((label, f"rc={rc} stderr={err[:500] if err else ''}"))

    # --- HTTP server + requests ---
    try:
        import requests
    except ImportError:
        _write(log_dir / "http-skipped.txt", "requests not installed\n")
        issues.append(("http", "requests module missing"))
        matrix.append(("HTTP", "all", "SKIP"))
    else:
        from shutil import which

        node = which("node")
        if not node:
            issues.append(("server", "node not on PATH"))
            matrix.append(("HTTP", "server", "SKIP"))
        else:
            port = _pick_port()
            base = f"http://{HOST}:{port}"
            srv_out = open(log_dir / "server-stdout.log", "w", encoding="utf-8", errors="replace")
            srv_err = open(log_dir / "server-stderr.log", "w", encoding="utf-8", errors="replace")
            proc = subprocess.Popen(
                [node, "dist/server.js"],
                cwd=WEB,
                stdout=srv_out,
                stderr=srv_err,
                env={**os.environ, "PORT": str(port), "HOST": HOST},
            )
            try:
                if not _wait_port(port):
                    issues.append(("server", f"did not listen on {HOST}:{port} in time"))
                    matrix.append(("HTTP", "listen", "FAIL"))
                else:
                    matrix.append(("HTTP", "listen", "PASS"))

                    def req(
                        method: str,
                        path: str,
                        *,
                        json_body: dict | None = None,
                        data: str | None = None,
                        headers: dict | None = None,
                    ) -> tuple[int, str]:
                        url = base + path
                        try:
                            if method == "GET":
                                r = requests.get(url, timeout=30)
                            elif method == "POST":
                                if data is not None:
                                    r = requests.post(
                                        url,
                                        data=data,
                                        headers=headers or {},
                                        timeout=180,
                                    )
                                else:
                                    r = requests.post(
                                        url,
                                        json=json_body,
                                        headers=headers or {"Content-Type": "application/json"},
                                        timeout=180,
                                    )
                            else:
                                raise ValueError(method)
                            body = r.text[:8000]
                            return r.status_code, body
                        except requests.RequestException as e:
                            return -1, str(e)

                    http_tests: list[tuple[str, str, str, dict | None, str | None, dict | None]] = [
                        ("GET /", "GET", "/", None, None, None),
                        ("GET /api/status", "GET", "/api/status", None, None, None),
                        ("GET /api/plans", "GET", "/api/plans", None, None, None),
                        ("GET /api/raw-data", "GET", "/api/raw-data", None, None, None),
                        ("GET /api/plan traversal", "GET", "/api/plan/../../../etc/passwd", None, None, None),
                        ("GET /api/plan missing", "GET", "/api/plan/does_not_exist_99999.json", None, None, None),
                        ("POST submit empty JSON", "POST", "/api/submit", {}, None, None),
                        ("POST submit empty query", "POST", "/api/submit", {"query": ""}, None, None),
                        ("POST submit whitespace query", "POST", "/api/submit", {"query": "   "}, None, None),
                        (
                            "POST submit invalid body",
                            "POST",
                            "/api/submit",
                            None,
                            "not-json-at-all",
                            {"Content-Type": "application/json"},
                        ),
                        (
                            "POST submit short query",
                            "POST",
                            "/api/submit",
                            {"query": "What is Python programming?"},
                            None,
                            None,
                        ),
                    ]

                    for name, method, path, jb, raw, hdrs in http_tests:
                        if method == "GET":
                            code, body = req("GET", path)
                        else:
                            if raw is not None:
                                code, body = req("POST", path, data=raw, headers=hdrs)
                            else:
                                code, body = req("POST", path, json_body=jb)
                        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", name)[:80]
                        _write(log_dir / f"http-{safe}.txt", f"status={code}\n\n{body}\n")
                        exp = "varies"
                        if (
                            "whitespace" in name.lower()
                            or name == "POST submit empty query"
                            or name == "POST submit empty JSON"
                        ):
                            st = "PASS" if code == 400 else f"UNEXPECTED({code})"
                        elif "invalid body" in name.lower():
                            st = "PASS" if code in (400, 500) else f"NOTE({code})"
                        elif "traversal" in name.lower():
                            # Express may normalize the path (400) or no file match (404)
                            st = "PASS" if code in (400, 404) else f"UNEXPECTED({code})"
                        elif "missing" in name.lower():
                            st = "PASS" if code == 404 else f"UNEXPECTED({code})"
                        elif "short query" in name.lower():
                            st = "PASS" if code == 200 else f"FAIL/BLOCKED({code})"
                            if code != 200:
                                issues.append(
                                    (name, f"status {code}; pipeline may need Ollama/Gemini — see body in log")
                                )
                        elif code == 200 or (path != "/api/submit" and code in (200, 400, 404)):
                            st = "PASS" if code >= 0 else "FAIL"
                        else:
                            st = f"HTTP {code}"
                        matrix.append(("HTTP", name, st))
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                srv_out.close()
                srv_err.close()

    # --- Report ---
    lines = [
        f"# Local varied-input run",
        f"",
        f"- UTC: `{ts}`",
        f"- Root: `{ROOT}`",
        f"- Python: `{sys.version.split()[0]}`",
        f"",
        f"## Result matrix",
        f"",
        f"| Area | Check | Result |",
        f"|------|-------|--------|",
    ]
    for a, c, r in matrix:
        lines.append(f"| {a} | {c} | {r} |")
    lines.extend(
        [
            f"",
            f"## Issues / bugs / errors (actionable)",
            f"",
        ]
    )
    if not issues:
        lines.append("None recorded automatically (see raw logs for warnings).")
    else:
        for title, detail in issues:
            lines.append(f"- **{title}**: {detail}")
    lines.extend(
        [
            f"",
            f"## Raw logs",
            f"",
            f"Directory: `{log_dir}`",
            f"",
        ]
    )
    _write(log_dir / "REPORT.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nFull report: {log_dir / 'REPORT.md'}")
    return 0 if not any(m[2].startswith("FAIL") for m in matrix if m[0] == "Phase 1") else 1


if __name__ == "__main__":
    raise SystemExit(main())
