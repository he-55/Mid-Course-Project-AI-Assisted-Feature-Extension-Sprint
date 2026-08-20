# Architectural Decision Record: In-Memory Data Storage

## Status
Accepted

## Context
The Task Tracker REST API requires an efficient, zero-configuration data store for rapid development, containerized deployment, and fast unit test execution.

## Decision
Utilize an in-memory Python dictionary (`_tasks: dict[int, dict]`) in `app/main.py` paired with `itertools.count(1)` for task ID allocation.

Provide a `reset_store()` helper function to reset stored state between unit tests.

## Trade-offs & Consequences
* **Benefits**: No database drivers or external setup required; instant test execution (< 0.3s for 47 unit tests); lightweight Docker build.
* **Limitations**: State is ephemeral and resets on application restart.
