# AI Prompt Log & Workflow Log

This document records the AI interaction loops used during the implementation of Due Dates + Overdue Filter and Tags / Labels.

Each loop follows the same workflow: **structured prompt → AI implementation → automated tests → live browser verification → human review/acceptance**. Prompts were written as mini-specs with explicit CONTEXT / OBJECTIVE / STYLE & TONE / RESPONSE STRUCTURE sections; that structure is noted below because output precision tracked prompt precision throughout the sprint (see [reflection.md](reflection.md)).

---

## Loop 0 — Baseline: Kanban board scaffold

**Prompt (summary).** Full spec for a FastAPI + Vanilla JS Kanban tracker: three columns, HTML5 drag-and-drop, strictly unidirectional state flow (`To Do → In Progress → Done`, never back to To Do, enforced on UI *and* API with HTTP 400), full CRUD, pytest suite including a health check and illegal-transition tests. Response structure mandated file-by-file output.

**AI output.** `schemas.py` (Pydantic v2 models + `STATUS_ORDER` rank map), `main.py` (in-memory store, CRUD routes, `validate_transition()`), `static/index.html` + `static/app.js` (board, drag-and-drop with legal/illegal drop highlighting), `test_main.py` (18 tests), venv + requirements.

**AI interpretation of ambiguity.** "Strictly unidirectional" was resolved as: any move to a lower rank is illegal (so `done → in_progress` is also blocked), forward skips (`todo → done`) allowed, same-status no-ops allowed. Accepted after review.

**Verification.** 18/18 tests passed; AI launched the server, created a task through the real form, and screenshotted the board.

## Loop 1 — Feature: Due Dates + Overdue Filter

**Prompt (summary).** Add optional `due_date` (ISO 8601) to models and CRUD; card badges; red overdue styling (past due AND not Done), orange due-soon (24–48 h), completed tasks must never look urgent; a filter bar (All / Overdue / Due Soon / No Due Date) working client-side without reloads; tests for valid/invalid payloads and filtering logic.

**AI output.** `due_date: Optional[date]` across schemas (Pydantic handles ISO parsing/422s); `is_overdue()` / `is_due_soon()` predicates with `DUE_SOON_WINDOW_DAYS = 2`; `?due=overdue|soon|none` API filter; PATCH distinguishing absent field (preserve) from explicit `null` (clear) via `model_fields_set`; filter pills, badges, and a timezone-safe client-side date comparison (lexicographic `YYYY-MM-DD` strings instead of `new Date()` parsing). 14 new tests → 32 total.

**Verification.** 32/32 passed. Browser: seeded past/near/future/undated tasks; confirmed red overdue badge, orange due-soon, green neutral badge on a Done task with a past date, and the Overdue pill excluding Done tasks.

**Human intervention.** Manual testing on the live board between loops — a hand-created overdue In-Progress task ("this is an overdue task") later surfaced in the AI's own counter check ("Showing 1 of 6"), forcing it to reconcile against state it did not seed. Styling and filters held.

## Loop 2 — Feature: Real-time search (supporting both features)

**Prompt (summary).** Client-side search bar with icon + clear button; `/` and Ctrl/Cmd+K shortcuts; 150–200 ms debounce; case-insensitive matching over title and description with highlighted matches; per-column empty states; "Showing X of Y" counter; must compose with the existing due-date filters.

**AI output.** Debounced (180 ms) DOM-only search pass layered over the render pipeline ("pills decide which cards exist; search decides which are shown"), DOM-node-based `<mark>` highlighting (no innerHTML → no injection), keyboard handling that ignores `/` while typing in inputs, counter + empty-state logic.

**Verification.** Browser: `/` focused input; "invoice" highlighted and narrowed the board; Overdue pill × query composed correctly; ✕ restored state. Suite re-run as regression: 32/32.

## Loop 3 — Documentation gap → Feature: Tags / Labels

**Prompt (summary).** A requested `user-stories.md` referenced "Tags / Labels" — a feature that did not exist yet. The AI flagged the doc/reality gap; the human directed: *"do both, start with the user stories."*

**AI output.** First the user stories (9 stories, 30 acceptance criteria, traceability table), then the implementation to match them: `tags: list[str]` with server-side normalization (trim/lowercase/dedupe, ≤30 chars, ≤10 tags, 422 otherwise); `?tag=` case-insensitive API filter composing with `?status=`/`?due=`; deterministic-color chips (string hash → 6 hues); click-chip-to-filter with a `tag: x ✕` clear pill; tags folded into the search index. 11 new tests → 43 total.

**Verification.** 43/43 passed. Browser: chip colors consistent per tag; chip click narrowed board with counter + empty states; tag filter × search composed; query "bug" matched a card by tag alone (word absent from title/description).

**Notable ordering.** Writing testable acceptance criteria *before* implementing kept the spec honest — the doc drove the code rather than describing it after the fact.

## Loop 4 — Evidence & closure

**Prompts.** Create `verification.md` and `prompt-log.md` stubs; run a Q&A to gather the human's own views; write `reflection.md` (250–500 words) from those answers; populate both logs with real evidence.

**AI output.** Live break tests against the running server (illegal move → 400 with unchanged state; malformed date, empty tag, 11 tags, unknown filter → 422), captured with the final 43-test suite run in [verification.md](verification.md); a 460-word first-person reflection built from the Q&A answers; this log.

---

## Workflow observations

- **The loop that held every time:** spec → generate → pytest → live browser check → human acceptance. No increment was accepted on generation alone.
- **Tests as the contract:** each feature landed with its negative cases (400/422) in the same commit-sized increment, so regressions were caught by re-running one suite (0.2 s).
- **Human review changed outcomes** at two points: independent manual testing with un-seeded data (Loop 1), and catching the docs-ahead-of-code gap that became the Tags feature (Loop 3).
