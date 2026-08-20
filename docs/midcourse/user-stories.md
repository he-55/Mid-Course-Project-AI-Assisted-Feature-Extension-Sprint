# User Stories: AI-Assisted Feature Extension Sprint

This document defines the user stories and testable acceptance criteria for the two extended features: Due Dates + Overdue Filter and Tags / Labels.

Conventions used below:

- **AC** = acceptance criterion, written as Given / When / Then and phrased so it can be verified by an automated test or a scripted manual check.
- Statuses flow strictly `To Do → In Progress → Done` (pre-existing invariant; the features below must never weaken it).
- "Urgency styling" means the red (overdue) / orange (due soon) card treatments.

---

## Feature 1: Due Dates + Overdue Filter

### Story 1.1 — Set a due date when creating a task

> As a board user, I want to optionally attach a due date when I create a task, so that time-sensitive work is captured at entry time.

**Acceptance criteria**

- **AC 1.1.1** — Given the create form, when I submit a task with a valid `YYYY-MM-DD` due date, then the API returns 201 and the response contains `due_date` in ISO 8601 format.
- **AC 1.1.2** — Given the create form, when I submit a task without a due date, then the task is created with `due_date: null`.
- **AC 1.1.3** — Given a create request with a malformed date (`"not-a-date"`, `"31/12/2026"`, `"2026-13-01"`, a number), then the API rejects it with HTTP 422 and no task is created.

### Story 1.2 — Edit or clear a due date

> As a board user, I want to change or remove a task's due date after creation, so that plans can adapt.

**Acceptance criteria**

- **AC 1.2.1** — Given an existing task, when I PATCH a new valid `due_date`, then the response reflects the new date.
- **AC 1.2.2** — Given a task with a due date, when I PATCH `"due_date": null` explicitly, then the date is cleared.
- **AC 1.2.3** — Given a task with a due date, when I PATCH other fields *without* mentioning `due_date`, then the existing date is preserved (absent ≠ null).
- **AC 1.2.4** — Given a PATCH with a malformed date, then the API returns 422 and the task is unchanged.

### Story 1.3 — See overdue tasks at a glance

> As a board user, I want overdue tasks visually flagged in red, so that slipping work is impossible to miss.

**Acceptance criteria**

- **AC 1.3.1** — Given a task whose due date is before today and whose status is not Done, then its card shows red urgency styling (left border + red "Overdue" badge).
- **AC 1.3.2** — Given a task due within the due-soon window (today through today + 2 days) and not Done, then its card shows orange "Due soon" styling.
- **AC 1.3.3** — Given a Done task with a past due date, then it shows **no** urgency styling — a neutral green date badge only. Completed work never reads as urgent.
- **AC 1.3.4** — Given a task with no due date, then no date badge is rendered.

### Story 1.4 — Filter the board by timeline

> As a board user, I want one-click timeline filters (Overdue, Due Soon, No Due Date), so that I can focus on what needs attention now.

**Acceptance criteria**

- **AC 1.4.1** — Given the filter bar, when I select **Overdue**, then only tasks past their due date and not Done remain visible; Done tasks with past dates are excluded.
- **AC 1.4.2** — When I select **Due Soon**, then only not-Done tasks due between today and the window edge (inclusive) remain visible.
- **AC 1.4.3** — When I select **No Due Date**, then only undated tasks remain visible.
- **AC 1.4.4** — The same semantics are available server-side via `GET /api/tasks?due=overdue|soon|none`, composable with `?status=`; an unknown `due` value returns 422.
- **AC 1.4.5** — Filtering happens client-side without a page reload, and per-column counts update to the visible number.

---

## Feature 2: Tags / Labels

### Story 2.1 — Assign tags when creating a task

> As a board user, I want to attach one or more short tags (e.g. `frontend`, `bug`, `api`) when creating a task, so that work can be categorized across columns.

**Acceptance criteria**

- **AC 2.1.1** — Given the create form, when I submit a task with comma-separated tags, then the API returns 201 and the response contains the tags as a list.
- **AC 2.1.2** — Tags are normalized server-side: trimmed, lowercased, and de-duplicated (order-preserving). `"API, api , Frontend"` is stored as `["api", "frontend"]`.
- **AC 2.1.3** — A task created without tags has `tags: []`.
- **AC 2.1.4** — Invalid tag payloads are rejected with 422: a tag that is empty/whitespace-only, a tag longer than 30 characters, or more than 10 tags on one task.

### Story 2.2 — Edit a task's tags

> As a board user, I want to change a task's tags after creation, so that categorization stays accurate.

**Acceptance criteria**

- **AC 2.2.1** — Given an existing task, when I PATCH a `tags` list, then it **replaces** the previous list wholesale (no implicit merging).
- **AC 2.2.2** — When I PATCH `"tags": []`, then all tags are removed.
- **AC 2.2.3** — When I PATCH other fields without mentioning `tags`, then the existing tags are preserved.
- **AC 2.2.4** — Normalization and validation rules from AC 2.1.2 / 2.1.4 apply equally on update.

### Story 2.3 — See tags on task cards

> As a board user, I want each card to display its tags as colored chips, so that categories are scannable at a glance.

**Acceptance criteria**

- **AC 2.3.1** — Each tag renders as a small colored chip on the card, below the title/description.
- **AC 2.3.2** — Chip color is deterministic per tag name (same tag → same color everywhere on the board).
- **AC 2.3.3** — Cards without tags render no chip row (no empty container).

### Story 2.4 — Filter the board by tag

> As a board user, I want to click a tag chip to see only tasks carrying that tag, so that I can slice the board by category.

**Acceptance criteria**

- **AC 2.4.1** — Clicking a chip activates a tag filter; only tasks with that tag remain visible across all columns, without a page reload.
- **AC 2.4.2** — An active-tag indicator appears in the filter bar (e.g. `tag: api ✕`) and clicking it clears the tag filter.
- **AC 2.4.3** — The same filter is available server-side via `GET /api/tasks?tag=<name>`, matching case-insensitively.
- **AC 2.4.4** — The tag filter composes with `?status=` and `?due=` on the API, and with the due-date pills **and** the search box in the UI (intersection semantics: a card must satisfy all active filters).

### Story 2.5 — Search includes tags

> As a board user, I want the search box to also match tag names, so that typing `api` finds tagged work even when the word appears nowhere in the title or description.

**Acceptance criteria**

- **AC 2.5.1** — A search query matches against title, description, and tag names (case-insensitive).
- **AC 2.5.2** — The match counter, per-column counts, and empty states account for tag-filter and search visibility combined.

---

## Traceability

| Criterion | Verified by |
|---|---|
| AC 1.1.x, 1.2.x | `tests/test_main.py` — due-date create/update/clear/preserve/422 tests |
| AC 1.3.x | Manual browser check (screenshots in `docs/verification.md`) |
| AC 1.4.1–1.4.4 | `tests/test_main.py` — `due` filter tests incl. Done-exclusion and 422 |
| AC 1.4.5 | Manual browser check |
| AC 2.1.x, 2.2.x | `tests/test_main.py` — tag create/update/normalization/422 tests |
| AC 2.3.x | Manual browser check |
| AC 2.4.3, 2.4.4 (API) | `tests/test_main.py` — `tag` filter tests incl. composition |
| AC 2.4.1, 2.4.2, 2.4.4 (UI), 2.5.x | Manual browser check |
