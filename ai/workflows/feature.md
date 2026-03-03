# Feature Workflow Blueprint

## Intent
Standardized process for implementing new features into the Mexican Online Stock Trading Retail Brokerage.

## Steps
1. **Decisions (Guardrails)**:
   - Read `docs/decisions/` and list which decisions apply.
   - If implementation requires a new cross-cutting pattern not covered:
     - Draft a new decision record with **Status: Proposed** and stop for human approval.
   - If a decision conflicts with the feature spec, stop and escalate to human.
2. **Spec Creation**: Human creates ephemeral feature spec in `docs/features/<name>.md`.
3. **Planning**: Run `ai/agents/planner.md` with the feature spec to produce an implementation plan.
4. **Database**: Run `ai/agents/db.md` for schema and migrations.
5. **Backend**: Run `ai/agents/backend.md` for API and tests.
6. **Frontend**: Run `ai/agents/frontend.md` for UI and UX.
7. **Review**: Run `ai/agents/reviewer.md` on the completed diffs.
8. **Verification**: Run `ai/agents/qa.md` to produce a verification script.
