# Plan
Read docs/features/<name>.md. Produce an implementation plan with DB/API/UI/test tasks. Ask questions only if blocked; otherwise make explicit assumptions.

# DB
Implement DB changes from plan: tables, constraints, indexes, migration + rollback notes.

# Backend
“Implement endpoints + validation + auth + tenant scoping. Add tests for acceptance criteria.”

# Frontend
“Build UI: contacts list/search/create/edit + account contacts section. Add loading/error/empty states.”

# Review
“Review the entire diff as staff engineer. Focus on security, simplicity, correctness, and consistency with repo patterns.”

# QA
“Generate a manual QA checklist + a few curl examples + edge case tests for X.”
