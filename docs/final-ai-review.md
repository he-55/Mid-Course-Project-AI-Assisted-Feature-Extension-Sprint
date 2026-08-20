# Final AI Review and Ownership Evidence

This document provides the official AI governance audit, AGENTS.md guardrail confirmation, AI code review mini-log, AI security mini-review, manual security check, rejected AI recommendations, three AI usage rules, and ownership statement.

---

## AGENTS.md guardrails
- **Repo-specific stack and commands included**: yes
- **Docs-first/read-first guardrail included**: yes
- **Unexpected app/frontend edits rule included**: yes

*Detailed Confirmation*: Adherence to all repository guardrails in [AGENTS.md](file:///Users/aminem/www/hiba-project/AGENTS.md) was strictly maintained throughout development. AI tools operated under read-only default constraints, core code was protected, and every code edit was empirically verified.

*Repository Structure Context*: Note that there is no `app/` directory or `frontend/` directory in this codebase. `main.py` and `schemas.py` are located at the repository root, and the Kanban frontend resides in `static/` (`static/index.html`). The guardrail restricting unexpected source/frontend edits applies directly to `main.py`, `schemas.py`, and `static/`. Zero unexpected changes were made to these core files.

---

## AI code review mini-log

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
| :--- | :--- | :--- | :--- |
| Scaffold Pydantic v2 `TaskCreate` and `TaskUpdate` models with field validators. | **Useful** | Correctly generated string constraints (`min_length=1`, `max_length=200`) in [schemas.py:L12-L25](file:///Users/aminem/www/hiba-project/schemas.py#L12-L25), ensuring data hygiene. | **Accepted**: Integrated schema definitions into [schemas.py](file:///Users/aminem/www/hiba-project/schemas.py). |
| Add SQLAlchemy dependency and SQLite database migrations for task persistence. | **Noise** | Unnecessary overhead. System specs mandate in-memory dictionary repository `_tasks` in [main.py:L18](file:///Users/aminem/www/hiba-project/main.py#L18). | **Rejected**: Kept lightweight in-memory storage dictionary. |
| Allow status transitions from `in_progress` back to `todo` and store `is_overdue` as a dict boolean. | **Wrong** | Violated unidirectional workflow rule ([AGENTS.md Section 3](file:///Users/aminem/www/hiba-project/AGENTS.md#L35)) and caused stale overdue flags when dates passed. | **Rejected**: Implemented strict forward validation and dynamic date evaluations in [main.py:L26-L45](file:///Users/aminem/www/hiba-project/main.py#L26-L45). |

---

## AI security mini-review

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
| :--- | :--- | :--- | :--- | :--- |
| **Root User Container Execution**: Base Docker build ran runtime stage as `root`. | [Dockerfile:L34](file:///Users/aminem/www/hiba-project/Dockerfile#L34) | **Valid** | Privilege escalation vulnerability if container is compromised. | **Remediated**: Created `appgroup` group and `app` user (`USER app`). |
| **Unbounded Input Strings**: Task title and description lacked character limits. | [schemas.py:L12-L25](file:///Users/aminem/www/hiba-project/schemas.py#L12-L25) | **Valid** | Potential memory exhaustion or HTML script payload injection. | **Remediated**: Added `min_length=1`, `max_length=200` for titles, `max_length=2000` for descriptions. |
| **Plaintext Credential Leak in Memory**: Flagged `_tasks` dict as storing unencrypted auth credentials. | [main.py:L18](file:///Users/aminem/www/hiba-project/main.py#L18) | **False Positive / Noise** | Application contains no authentication tokens, passwords, or credentials; tasks are public entities. | **Dismissed**: Marked as N/A in security audit. |

---

## Manual security check

I manually inspected the running application container context by executing `docker exec tt-app whoami` to confirm process privilege dropping to `app`. Additionally, I probed the API endpoints with boundary payloads (empty strings, illegal state rollbacks from `in_progress` to `todo`, and past due dates) via cURL and Swagger UI (`/docs`). This manual check verified that schema validation blocks empty titles (`HTTP 422`), state machine governance prevents backward status movement (`HTTP 400`), and dynamic timeline calculations correctly classify overdue tasks without storing stale booleans.

---

## One AI output I rejected or corrected

I rejected an AI recommendation that suggested running the Docker container process as `USER root` and storing a static `is_overdue` boolean inside the `_tasks` state dictionary. Running as root exposed the host environment to container breakout risks, while storing a static boolean caused stale data bugs when system dates advanced without task updates. Instead, I introduced an unprivileged system user (`USER app`) in [Dockerfile:L34](file:///Users/aminem/www/hiba-project/Dockerfile#L34) and refactored timeline logic into dynamic evaluation functions (`is_overdue`, `is_due_soon`) in [main.py:L26-L45](file:///Users/aminem/www/hiba-project/main.py#L26-L45) that calculate status on-the-fly and automatically exclude completed (`done`) tasks.

---

## Three AI usage rules

1. **Never paste**: API keys, `.env` secrets, database credentials, production logs, or personal customer data into AI prompts or repository files.
2. **Always verify**: Execute unit test suites (`pytest -v`), inspect diffs line-by-line, and verify container security context (`docker exec tt-app whoami`) before staging or merging code.
3. **Record AI contributions by**: Explicitly documenting AI suggestions, model tools used, graded findings, and human architectural overrides in [docs/final-ai-review.md](file:///Users/aminem/www/hiba-project/docs/final-ai-review.md).

---

## Ownership statement

I am completely comfortable submitting this repository as my own work. While AI tools assisted in drafting initial code templates, unit tests, and documentation formatting, every line of code, Docker configuration choice, and API contract was inspected, tested, and validated by me. I understand the entire system architecture, from Pydantic schema validation and state machine governance to non-root container deployment, and I accept full responsibility for all engineering decisions, code quality, and security controls in this project.
