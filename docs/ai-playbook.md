# Personal AI Coding Playbook & Governance Framework

This playbook defines non-negotiable rules, tool selection frameworks, review routines, and decision checklists for responsible AI-assisted software development.

---

## When I reach for AI first

* **Boilerplate & Schema Scaffolding**: Drafting initial Pydantic models, FastAPI CRUD route skeletons, and basic HTML form structures.
* **Test Case Expansion**: Generating repetitive test payload variations and boundary assertion boilerplate for Pytest test suites.
* **Syntax & Configuration Generation**: Writing multi-stage `Dockerfile` templates, GitHub Actions `ci.yml` workflows, and complex regular expressions.
* **Documentation Drafting**: Synthesizing architecture diagrams (Mermaid format), release summaries, and API reference tables from existing code contracts.

---

## When I do not reach for AI first

* **State Machine & Business Rules**: Defining core domain constraints such as unidirectional status transitions (`todo` -> `in_progress` -> `done`).
* **Security & Permission Boundaries**: Configuring container non-root system users (`USER app`) and privilege boundaries.
* **Ambiguous Diagnostic Troubleshooting**: Resolving complex bugs where root cause spans multiple subsystems (e.g. dynamic timeline calculations vs state dictionary storage).
* **Final Code Approvals & Merges**: Reviewing diffs line-by-line and taking final ownership of code merged into production.

---

## My non-negotiables

1. **Never Paste Secrets or Personal Data**: Never output, commit, or prompt with API keys, tokens, `.env` file secrets, database credentials, production logs, or personal customer data.
2. **Empirical Verification Required**: Never mark a task resolved without running actual verification commands (`pytest -v`, Docker container health checks).
3. **Root Cause Resolution**: Reject quick symptom-masking fixes such as commenting out failing assertions, inserting silent exception handlers, or returning fallback defaults.
4. **Context Grounding**: Always ground instructions in actual relative file paths ([main.py](file:///Users/aminem/www/hiba-project/main.py), [schemas.py](file:///Users/aminem/www/hiba-project/schemas.py), [static/index.html](file:///Users/aminem/www/hiba-project/static/index.html)) and concrete system schemas.

---

## My review rules

1. **Line-by-Line Diff Inspection**: Inspect every proposed git diff before staging or committing changes. Check that existing API contracts and schema limits remain unchanged.
2. **Execute Local Verification**: Always execute `.venv/bin/pytest -v` and inspect terminal output before accepting AI code proposals.
3. **Grade & Classify Findings**: Classify all AI suggestions as `Useful`, `Noise`, or `Wrong`, rejecting any proposal that adds unnecessary dependencies or violates system guardrails.
4. **Container Security Audit**: Verify container execution context using `docker exec <container> whoami` to ensure processes run as non-root users (`app`).

---

## What I am still figuring out

* **Long-Context Token Optimization**: Balancing whole-repository context loading against token consumption during extended debugging sessions.
* **Automated Documentation Synchronization**: Streamlining mechanisms to keep external markdown documentation ([docs/](file:///Users/aminem/www/hiba-project/docs)) automatically in sync with rapid source code edits.
* **Optimal Prompt Strategies for Multi-File Refactoring**: Crafting prompt structures that perform complex multi-file refactoring without context drift or unintended API contract breaks.

---

## Decision Card

```text
===========================================================================
                     AI IMPLEMENTATION DECISION CARD
===========================================================================
1. TASK CLASSIFICATION & STRATEGY SELECTION
   [ ] New Feature: Is it boilerplate or CRUD scaffolding?
       --> REACH FOR AI FIRST (Accelerate initial draft creation)
   [ ] Code Review & Refactoring: Does it touch state machine or security?
       --> HUMAN DESIGN FIRST (Draft constraints manually before AI assistance)
   [ ] Infrastructure & CI: Is it standard Docker or GitHub Actions setup?
       --> REACH FOR AI FIRST (Scaffold config, then audit manually)
   [ ] Debugging: Is the failure root cause ambiguous or multi-layered?
       --> HUMAN ANALYSIS FIRST (Read full logs before asking AI)

2. GROUNDING & CONTEXT CHECKLIST
   [ ] Are exact relative file paths provided in the prompt?
   [ ] Are schema constraints (min/max lengths, types) explicitly defined?
   [ ] Is the request isolated to a single bounded task?
   [ ] Rule: NEVER PASTE secrets, tokens, .env files, or real user data.

3. DIFF INSPECTION & REVIEW RULES
   [ ] Have all proposed file diffs been reviewed line-by-line?
   [ ] Are existing API contracts and schema structures preserved?
   [ ] Are there any hidden side-effects or silent exception handlers?

4. VERIFICATION & VALIDATION
   [ ] Did the test suite execute cleanly (`pytest -v`)?
   [ ] Were container/runtime checks performed successfully (`whoami` -> app)?
   [ ] Does the implementation meet all AGENTS.md guardrails?
===========================================================================
```
