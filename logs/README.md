# Logs directory

## `local-test/` (gitignored)

Ad-hoc full local test output from [implementationtest.md](../implementationtest.md)–style runs: per-phase `*.log`, HTTP captures `*.json` / `*.txt`, optional `server.pid`, and [local-test/summary.md](local-test/summary.md).

This folder is listed in [.gitignore](../.gitignore) so large or machine-specific artifacts are not committed.

### Conventions

- **Server logs:** Capture may produce `server-stdout.log`, `server-stdout2.log`, or a separate `server-stderr.log` depending on how you redirect streams. The summary index should list **files that actually exist** for that run.
- **PowerShell:** Do not assign to `$PID` / `$pid` when saving a process id from a file — use e.g. `$serverPid = Get-Content ...`.
- **pip / `lxml` on Windows:** A clean install needs Python **3.10–3.12** (see [README.md](../README.md)); Python **3.14** often fails building `lxml` without libxml2 development headers.
