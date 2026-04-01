# Phase 01 - Repository Baseline

## Objective
Establish a clean, reproducible local baseline for development.

## Scope (in/out)
- In: dependency install, environment bootstrap, baseline checks.
- Out: feature implementation.

## Prerequisites
- Python and Node installed.
- Repository cloned.

## Implementation Steps
1. Install Python and Node dependencies.
2. Create `.env` from `.env.example`.
3. Verify project structure and key scripts.

## Deliverables
- Working local setup.
- Baseline verification notes.

## Verification Checklist
- `pip install -r requirements.txt` succeeds.
- `cd web && npm install` succeeds.

## Risks and Rollback Notes
- Risk: version mismatch.
- Rollback: pin supported runtime versions.

## Exit Criteria
Environment is runnable from repo root.

## Handoff to Next Phase
Proceed to core configuration and validation setup.

