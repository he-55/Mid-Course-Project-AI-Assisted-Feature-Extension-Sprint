# System Architecture & Context Engineering Synthesis

This document details the architectural layout, core backend and frontend components, data flow, and context engineering analysis for the Task Tracker application.

---

## 1. System Context Diagram

```mermaid
flowchart TD
    User["Web Browser Client"] -->|HTTP / JSON| WebUI["Kanban Frontend (static/index.html)"]
    WebUI -->|REST API Requests| API["FastAPI Service (main.py)"]
    API -->|Schema Validation| Validation["Pydantic Models (schemas.py)"]
    API -->|In-Memory Persistence| Repository["In-Memory Task Store (_tasks dict)"]
```

---

## 2. Component Design & Responsibilities

### Backend Infrastructure (`main.py` & `schemas.py`)
- **App Configuration**: FastAPI instance configured with metadata, healthcheck route (`/health`), root page (`/`), and static directory mount (`/static`).
- **REST Endpoints**: Full CRUD endpoints under `/api/tasks` supporting task creation, listing, detail retrieval, partial updates, and deletion.
- **Validation Engine**: Pydantic v2 schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`) ensuring string length limits, tag counts (max 10), tag length (max 30), and ISO date formatting.
- **State Guardrails**: `validate_transition()` function preventing illegal state rollbacks (`todo` -> `in_progress` -> `done`).

### Frontend Interface (`static/index.html`)
- Responsive Kanban layout providing interactive task creation modals, column views, hashtag chip tags, timeline filters, and status transitions.

---

## 3. Context Engineering Performance Comparison

| Prompt Strategy | Context Provided | Result Quality & Accuracy |
| :--- | :--- | :--- |
| **Strategy A (Minimal)** | Broad instruction without file pointers | Generic code requiring manual adjustments to fit workspace |
| **Strategy B (Structured)** | Prompt including schema bounds & validation rules | Functional code matching schema definitions |
| **Strategy C (Targeted Grounded)** | Detailed prompt with file paths, schemas, and test requirements | High-quality implementation passing all unit tests cleanly on first attempt |
