# Phase 03 - CI Parity Validation

## Objective
Match local validation to CI baseline checks.

## Scope (in/out)
- In: test scripts and web build parity.
- Out: deployment.

## Prerequisites
- Phases 01-02 completed.

## Implementation Steps
1. Run basic Python tests.
2. Run comprehensive Python tests.
3. Build web bundle with CI-equivalent commands.

## Deliverables
- Test execution logs.
- Build artifacts in expected locations.

## Verification Checklist
- `python test_basic.py` passes.
- `python test_comprehensive.py` passes.
- `cd web && npm ci && npm run build` passes.

## Risks and Rollback Notes
- Risk: flaky environment dependencies.
- Rollback: clear venv/node modules and reinstall.

## Exit Criteria
All CI-equivalent checks pass locally.

## Handoff to Next Phase
Start provider-mode and planning path checks.

