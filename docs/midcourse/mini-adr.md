# Mini Architecture Decision Record (Mini-ADR)

**Title:** Implementation Strategy for Due Dates, Overdue Filter, and Tags Features
**Status:** Approved
**Context:** Mid-Course Project Sprint

## Context

The baseline application is a FastAPI + Vanilla JS Kanban tracker with an in-memory store, a strict unidirectional status flow (`todo → in_progress → done`), and a pytest suite. The sprint extends it with due dates, timeline filtering, real-time search, and tags — without introducing frontend frameworks, an ORM, or third-party search libraries, and without weakening the existing state-transition contract.

## Decisions

### D1 — Types over strings for dates: Pydantic v2 `date` fields

`due_date` is `Optional[date]`, not a string. Pydantic gives ISO 8601 parsing, `"YYYY-MM-DD"` serialization, and 422 rejection of malformed input for free; route code compares real `date` objects.
*Alternative rejected:* string field + hand-rolled regex validation — more code, weaker guarantees, timezone-ambiguous comparisons.

### D2 — Urgency is derived, never stored

"Overdue" and "due soon" are computed at read time (`is_overdue()` / `is_due_soon()` against `date.today()`, window constant `DUE_SOON_WINDOW_DAYS = 2`), not persisted as flags. Both predicates exclude `done` tasks by definition, which is what guarantees "completed work never looks urgent" everywhere — filters and UI alike.
*Alternative rejected:* a stored `is_overdue` flag — would require a background job or recompute-on-write and can go stale at midnight.

### D3 — Partial-update semantics: absent ≠ null

PATCH distinguishes "field not sent" (preserve) from explicit `null` (clear) using Pydantic's `model_fields_set` for `due_date`. Tags avoid the mechanism entirely: `None` means untouched, and a sent list — including `[]` — replaces wholesale. No merge semantics.
*Alternative rejected:* treating `None` as "no change" for due dates — would make a due date impossible to clear via the API.

### D4 — Filtering logic exists in both tiers, from one definition

The backend exposes `?status=` / `?due=` / `?tag=` (intersection semantics, unknown values → 422) as the authoritative, machine-usable contract. The frontend mirrors the same predicates client-side (rank map, due-window, tag membership) so the board filters without reloads. Shared constants (`STATUS_ORDER`, due-soon window) are duplicated knowingly, with tests pinning the backend as the source of truth.
*Alternative rejected:* refetching from the API on every filter/search interaction — simpler consistency, but visible latency on every keystroke and against the "seamless, no reload" requirement.

### D5 — Search is a DOM pass layered over rendering

Rule: *pill/tag filters decide which cards exist in the DOM; search decides which are shown.* Every render path ends with `applySearch()` — a pure DOM pass (180 ms debounce) that toggles visibility, rebuilds `<mark>` highlights from `dataset` values using DOM nodes (never `innerHTML`, so task content cannot inject markup), and recomputes counts/empty states. Client-side dates are compared as `"YYYY-MM-DD"` strings lexicographically, avoiding `new Date("…")` UTC-midnight parsing bugs near day boundaries.
*Alternative rejected:* re-rendering the whole board per keystroke — loses input focus and animation state, and does more work than toggling classes.

### D6 — Tags are normalized once, server-side

Trim, lowercase, order-preserving dedupe; limits (≤ 30 chars, ≤ 10 per task) enforced by one `normalize_tags()` validator shared by create and update. Because stored tags are canonical lowercase, `?tag=` matching is trivially case-insensitive and the UI never needs fuzzy comparison. Chip colors are a pure function (string hash → 6 hue classes), so identical tags render identically with zero stored color state.
*Alternative rejected:* a separate `Tag` entity with IDs and a join — right for multi-board/rename features, overkill for this sprint's in-memory store.

## Consequences

**Positive.** Validation lives in schemas, not routes; every rule is testable in isolation (47 passing tests, including 400/422 negative cases); the UI stays dependency-free; urgency can never desynchronize from the calendar; the API remains the single authority a non-browser client can rely on.

**Negative / accepted trade-offs.** In-memory store resets on restart (persistence is a known follow-up); duplicated filter predicates in JS must track backend changes (mitigated by tests + shared constants); whole-query substring search (no per-word AND) — a one-line upgrade point documented in the code; date-only granularity (no times/timezones) — "overdue" flips at local midnight.

## References

- Acceptance criteria: [user-stories.md](user-stories.md)
- Evidence for the guarantees above: [verification.md](verification.md)
- Interaction history: [prompt-log.md](prompt-log.md)
