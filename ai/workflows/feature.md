# Feature Workflow Blueprint

## Intent
Standardized process for implementing new features into the CRM.

## Steps
1. **Spec Creation**: Human creates ephemeral feature spec in `docs/features/<name>.md`.
2. **Planning**: Run `ai/agents/planner.md` with the feature spec to produce an implementation plan.
3. **Database**: Run `ai/agents/db.md` for schema and migrations.
4. **Backend**: Run `ai/agents/backend.md` for API and tests.
5. **Frontend**: Run `ai/agents/frontend.md` for UI and UX.
6. **Review**: Run `ai/agents/reviewer.md` on the completed diffs.
7. **Verification**: Run `ai/agents/qa.md` to produce a verification script.
