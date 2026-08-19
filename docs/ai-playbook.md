# Personal AI Coding Playbook & Governance Framework

This document outlines non-negotiable rules, tool selection frameworks, review routines, and decision checklists for AI-assisted software development.

---

## 1. Core Engineering Non-Negotiables

1. **Empirical Verification Required**: Never mark a task resolved without running actual verification commands (`pytest -v`, Docker health checks).
2. **Root Cause Resolution**: Reject quick symptom-masking fixes such as commenting out failing assertions or inserting silent exception handlers.
3. **Context Grounding**: Always ground instructions in actual file paths and concrete system schemas.

---

## 2. AI Implementation Decision Checklist

```text
===========================================================================
                     AI WORKFLOW CHECKLIST
===========================================================================
1. SPECIFICATION & CONTEXT
   [ ] Are the file paths, constraints, and schemas explicitly stated?
   [ ] Does the request fit into a single bounded task?

2. DIFF & CODE INSPECTION
   [ ] Have all proposed file diffs been reviewed line-by-line?
   [ ] Are existing API contracts and schema structures preserved?

3. VERIFICATION & VALIDATION
   [ ] Did the test suite execute cleanly (`pytest -v`)?
   [ ] Were container/runtime checks performed successfully?
===========================================================================
```

---

## 3. Operational Habits & Periodic Reminders

* **Daily Routine**: Run `git diff` before staging and committing code.
* **Sprint Routine**: Clean scratch artifacts and review GitHub Actions workflow logs.
* **Monthly Review**: Re-align `AGENTS.md` rules with evolving codebase conventions.
