# Phase 05 - Bridge Contract Validation

## Objective
Validate stdin/stdout JSON bridge behavior.

## Scope (in/out)
- In: `api_bridge.py` actions and response shape.
- Out: browser UX.

## Prerequisites
- Provider mode decided.

## Implementation Steps
1. Run `status` bridge action.
2. Run one `submit` smoke action.
3. Confirm JSON response contracts.

## Deliverables
- Bridge smoke outputs.

## Verification Checklist
- `echo '{"action":"status"}' | python api_bridge.py` returns `success: true`.

## Risks and Rollback Notes
- Risk: wrong Python interpreter.
- Rollback: set `PYTHON_EXE` or `TRUSTWISE_PYTHON`.

## Exit Criteria
Bridge status and submit actions are stable.

## Handoff to Next Phase
Validate Express API endpoints.

