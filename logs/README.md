# Logs Directory Guide

`logs/local-test/` stores local run artifacts and is gitignored.

## Typical Artifacts

- Server stdout/stderr captures
- API response snapshots
- Per-run verification notes

## Conventions

- Keep filenames stable per run (timestamp or run id).
- Do not commit machine-specific logs.
- Use UTF-8 output in test environments when possible.

## Related Docs

- [implementationtest.md](../implementationtest.md)
- [docs/deployment-readiness-report.md](../docs/deployment-readiness-report.md)

