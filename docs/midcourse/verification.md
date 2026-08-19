# Verification Log & Test Evidence

This document records the empirical testing results, baseline suite checks, manual browser verification checklist, behavior contract, and Break Test evidence for the sprint.

All evidence below was captured on **2026-08-04** against the code at the end of the sprint (due dates + timeline filters, real-time search, tags/labels). Environment: Python 3.13.2, FastAPI + Pydantic v2, pytest via `.venv`.

---

## 1. Baseline suite checks

The automated suite grew with each feature increment and was run green before every hand-off:

| Sprint stage | Tests | Result |
|---|---|---|
| Initial Kanban board (CRUD + state rules) | 18 | 18 passed |
| + Due dates & timeline filters | 32 | 32 passed |
| + Tags / labels | 43 | 43 passed |

Final run:

```
======================== 43 passed, 1 warning in 0.22s =========================
```

(The single warning is an upstream Starlette `TestClient` deprecation notice, unrelated to application code.)

## 2. Empirical testing results (automated)

Coverage by area — all PASSED in the final run of `test_main.py`:

| Area | Tests | Key assertions |
|---|---|---|
| Health check | 1 | `GET /health` → 200 `{"status": "ok"}` |
| CRUD | 11 | create defaults to `todo`; 422 on missing/empty title; list/get/patch/delete; 404s for missing IDs |
| State transitions | 6 | forward moves allowed; every backward move → 400; rejected move leaves task unchanged; same-status PATCH is a no-op |
| Due dates | 7 | ISO 8601 round-trip; 422 for 4 malformed date shapes on create and update; explicit `null` clears; absent field preserves |
| Timeline filters | 7 | `?due=overdue/soon/none` semantics; Done tasks excluded from overdue and due-soon; composes with `?status=`; unknown value → 422 |
| Tags | 11 | normalization (trim/lowercase/dedupe); 422 for empty tag, >30 chars, >10 tags; replace-wholesale update; `[]` clears; absent preserves; `?tag=` case-insensitive; composes with `?status=` + `?due=` |

Date fixtures are computed relative to `date.today()` and window bounds derive from `DUE_SOON_WINDOW_DAYS`, so tests do not go stale and track the constant if tuned.

## 3. Break Test evidence (live API)

Executed with `curl` against the running server (`uvicorn`, port 8000) on 2026-08-04 — deliberate attempts to violate the contract, with observed responses:

| # | Attack | Observed response |
|---|---|---|
| 1 | Move a task `in_progress → todo` | **HTTP 400** — `"Illegal state transition: 'in_progress' -> 'todo'. Tasks can only move forward (todo -> in_progress -> done)."` |
| 2 | Create with malformed due date `"31/12/2026"` | **HTTP 422** |
| 3 | Create with an empty tag `[""]` | **HTTP 422** |
| 4 | Create with 11 tags | **HTTP 422** |
| 5 | Query unknown filter `?due=yesterday` | **HTTP 422** |
| 6 | Re-read the task from break test 1 | status still `in_progress` — the rejected move mutated nothing |

## 4. Manual browser verification checklist

Performed in the live app at `http://localhost:8000` with seeded tasks (past, near, and future due dates; tagged and untagged; one Done task with a past date). ✔ = observed working.

- ✔ Board renders three columns with live counts; create form adds a task to To Do without reload
- ✔ Drag-and-drop: legal targets highlight green and accept; illegal targets highlight red and refuse the drop; illegal attempts toast the backend's 400 detail
- ✔ Overdue card (due yesterday, not Done): red left border + red "📅 Aug 3 · Overdue" badge
- ✔ Due-soon card (due tomorrow): orange border + "Due soon" badge
- ✔ Done card with past due date: neutral green badge, **no** urgency styling (completed-override)
- ✔ Undated card: no badge at all
- ✔ Filter pills (Overdue / Due Soon / No Due Date) hide non-matching cards client-side; per-column counts update; Overdue excludes the Done task
- ✔ Search: `/` and Ctrl/Cmd+K focus the input; typing filters live (180 ms debounce); matches highlighted in yellow `<mark>`; ✕ and Escape clear
- ✔ "Showing X of Y tasks" counter and per-column "No matching tasks" empty states appear whenever any filter/search is active
- ✔ Search × filter composition: query "invoice" + Overdue pill → exactly the one overdue matching task
- ✔ Tag chips render with deterministic per-tag colors ("api" identical on every card)
- ✔ Clicking a chip activates the `tag: api ✕` pill; board narrows to tagged tasks; clicking the pill clears
- ✔ Search matches tag names alone: query "bug" found a card whose title/description contain no such word
- ✔ Independent user testing: a manually created overdue In-Progress task (not AI-seeded) showed correct red styling and appeared in the Overdue filter

## 5. Behavior contract

The rules the implementation guarantees, each backed by the evidence above:

1. **Status flow is strictly unidirectional.** `todo → in_progress → done`, ranked; any move to a lower rank returns 400 and mutates nothing. Forward skips (`todo → done`) and same-status PATCHes are allowed.
2. **New tasks always start in `todo`.** The create payload cannot set a status.
3. **`due_date` is optional ISO 8601 (`YYYY-MM-DD`).** Malformed values are rejected with 422. On PATCH, an absent field preserves the date; an explicit `null` clears it.
4. **Overdue** = due date before today AND status ≠ Done. **Due soon** = due within today‥today+2 days (inclusive) AND status ≠ Done. **Done tasks are never urgent** — visually or in filters.
5. **Tags are normalized server-side**: trimmed, lowercased, de-duplicated (order-preserving); ≤ 30 chars each, ≤ 10 per task; violations → 422. PATCH replaces the list wholesale; `[]` clears; absent preserves.
6. **All list filters compose by intersection** — `?status=`, `?due=`, `?tag=` on the API; pills × tag × search in the UI — and unknown filter values are rejected with 422 rather than ignored.
7. **Frontend and backend enforce the same rules independently.** The UI blocks illegal drops and mirrors the urgency/filter logic, but the backend remains the authority (400/422) for any client.

## Traceability

Acceptance criteria for these behaviors are defined in [user-stories.md](user-stories.md); its traceability table maps each criterion to the automated tests in section 2 or the manual checks in section 4.
