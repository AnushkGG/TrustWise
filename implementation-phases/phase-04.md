# Phase 04 - LLM Provider Path Selection

## Objective
Confirm the target planning provider path (Ollama, Gemini, both, or mock).

## Scope (in/out)
- In: provider availability and mode selection.
- Out: downstream trust/storage changes.

## Prerequisites
- Previous phases completed.

## Implementation Steps
1. Validate configured provider in `.env`.
2. Verify provider reachability.
3. Run one plan generation smoke query.

## Deliverables
- Provider-mode decision and evidence.

## Verification Checklist
- `api_bridge.py` status shows expected provider fields.

## Risks and Rollback Notes
- Risk: provider unavailability.
- Rollback: use mock planning path for continuity.

## Exit Criteria
Chosen provider mode is validated and documented.

## Handoff to Next Phase
Proceed to bridge and API contract checks.

