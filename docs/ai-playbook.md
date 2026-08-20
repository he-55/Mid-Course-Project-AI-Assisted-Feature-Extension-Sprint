# Personal AI Coding Playbook & Governance Framework

This is my compact checklist for responsible AI-assisted work on this project.

## When I reach for AI first

- Boilerplate such as Pydantic schemas, CRUD route scaffolding, test-case variations, CI YAML, Docker templates, and documentation outlines.
- Repetitive refactors after I have defined the behavior and file boundaries.
- Explaining a failing test after I have read the traceback and reproduced it.

## When I do not reach for AI first

- State-machine, security, and permission decisions where I need to understand the risk before drafting code.
- Ambiguous failures where the repository, logs, or business context are incomplete.
- Final approvals, merges, and ownership decisions; I must be able to explain every accepted line.

## My non-negotiables

1. Never paste secrets, `.env` values, credentials, production logs, or personal/customer data.
2. Keep the existing scope and inspect the repository before changing `app/` or `frontend/`.
3. Verify behavior with tests, route checks, Docker checks, and a line-by-line diff review.
4. Record AI suggestions, my grade, the evidence, and the human decision.

## My review rules

1. Read the relevant code, tests, and project instructions before prompting.
2. Review the complete diff and check API contracts, validation bounds, error codes, and security boundaries.
3. Run `.venv/bin/python -m pytest -v`; test negative cases and one real end-to-end path.
4. Grade findings as Useful, Noise, or Wrong; reject silent fallbacks, unrelated dependencies, and unverified claims.

## What I am still figuring out

- How to keep long-running AI context useful without loading unrelated files.
- Which documentation checks should become automated tests.
- How to keep duplicated frontend/backend rules synchronized as the application grows.

## Decision Card

```text
NEW FEATURE       Define acceptance criteria and scope first; use AI for bounded scaffolding.
CODE REVIEW       Human design first for state/security; inspect every changed line.
DEBUGGING         Reproduce and read the full evidence before asking AI for hypotheses.
INFRASTRUCTURE    AI may draft CI/Docker; verify commands, versions, users, and secrets manually.
NEVER-PASTE       No keys, tokens, .env files, logs, or real user data.
PERSONAL RULE     If I cannot explain it, I do not submit it.
```
