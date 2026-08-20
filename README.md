# Task Tracker REST API & Kanban UI

A production-grade Task Tracker application powered by Python 3.11, FastAPI, Pydantic v2, and a responsive Vanilla JavaScript Kanban interface.

---

## Final Project

Branch reviewed: `final-project`

### What this submission demonstrates
- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally
```bash
pip install -r requirements.txt
python run.py
# OR
uvicorn app.main:app --reload
```

### How to run tests
```bash
pytest -v
# OR
.venv/bin/pytest -v
```

### How to run with Docker
```bash
docker build -t task-tracker .
docker run --rm -d -p 8000:8000 --name tt-app task-tracker
curl -s http://localhost:8000/health
```

### Evidence files
- [docs/release-evidence.md](docs/release-evidence.md)
- [docs/final-ai-review.md](docs/final-ai-review.md)
- [docs/ai-playbook.md](docs/ai-playbook.md)

### AI assistance summary
AI helped draft or review: CI workflow, Docker multi-stage setup, Pydantic schemas, Pytest unit test expansion, security audits, and documentation synthesis.  
I verified the work by: executing `pytest -v` (43/43 tests passing), verifying Docker container health and `whoami` non-root execution (`app`), auditing git index for secret/junk file leakage, and running cURL endpoint checks.  
One AI suggestion I rejected or corrected: Rejected AI proposal to run container as root (`USER root`); introduced non-root user `app:appgroup` in runtime stage of [Dockerfile](Dockerfile#L34). Also rejected stored boolean `is_overdue` in state dictionary in favor of dynamic evaluations in [main.py](main.py#L26-L45).

---

## 📌 Release Summary

| Key Metric / Property | Specification |
| :--- | :--- |
| **Git Branch** | `final-project` |
| **Repository URL** | [https://github.com/he-55/Mid-Course-Project-AI-Assisted-Feature-Extension-Sprint](https://github.com/he-55/Mid-Course-Project-AI-Assisted-Feature-Extension-Sprint) |
| **Backend Stack** | Python 3.11+, FastAPI 0.110+, Pydantic v2, Uvicorn |
| **Frontend Stack** | HTML5, Vanilla CSS3, JavaScript (Kanban Dashboard) |
| **Test Suite Status** | 43/43 Pytest Unit Tests Passing (100% Green) |

---

## ⚡ Core Application Features

1. **Kanban REST Operations**: Complete CRUD capabilities for tasks with real-time UI synchronization.
2. **Unidirectional Workflow Enforcer**: Tasks move strictly forward (`todo` -> `in_progress` -> `done`). Backward moves raise `HTTP 400 Bad Request`.
3. **Pydantic Validation**: Titles (1-200 chars), descriptions (up to 2000 chars), and ISO due dates (`YYYY-MM-DD`).
4. **Tag Management**: Up to 10 tags per task (max 30 chars each), automatically sanitized (trimmed, lowercased, deduplicated).
5. **Timeline Filtering**: Dynamic filtering by status, tag name, and timeline status (`overdue`, `soon`, `none`), excluding completed (`done`) tasks from overdue flags.
6. **OpenAPI Documentation**: Automatically generated interactive documentation at `/docs` (Swagger UI) and `/redoc`.
7. **Containerization & CI**: Multi-stage Docker container build running as an unprivileged system user (`USER app`), with continuous integration verified on GitHub Actions.

---

## 🛠️ Local Environment & Running

### Requirements
- **Python**: 3.11 or higher
- **Docker**: (Optional, for containerized execution)
- **Git**

### Installation & Local Launch

```bash
# Install required Python packages
pip install -r requirements.txt

# Option A: Run using the runner script
python run.py

# Option B: Run via Uvicorn directly
uvicorn app.main:app --reload --port 8000
```

Access the application endpoints in your browser:
- **Kanban Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Service Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Automated Unit Testing

The automated test suite consists of 43 unit tests verifying health endpoints, CRUD operations, state transition constraints, tag sanitization, and timeline calculations.

To run the full test suite:
```bash
pytest -v
```

---

## 🐳 Docker Container Deployment

The repository includes a production-oriented, multi-stage `Dockerfile` with non-root security isolation (`app:appgroup`) and health checking.

### Build Image
```bash
docker build -t task-tracker .
```

### Launch Container
```bash
docker run --rm -d -p 8000:8000 --name tt-app task-tracker
```

### Health & User Security Audit
```bash
# Check service health
curl -s http://localhost:8000/health

# Confirm non-root process user
docker exec tt-app whoami
# Output: app
```

### Stop Container
```bash
docker stop tt-app
```

---

## ⚙️ CI/CD Automation Pipeline

Automated testing is managed through GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)).

- **Triggers**: Pushes to `main`, `final-project`, `docs-update`, `'feature/**'`, and Pull Requests to `main`, `final-project`, `docs-update`.
- **Environment**: Python 3.11 on `ubuntu-latest`.
- **Pipeline Workflow**: Code checkout, Python environment configuration with pip caching, dependency installation, and `pytest -v` execution.

---

## 📁 Repository Directory Layout

```text
hiba-project/
├── AGENTS.md                  # Project instructions and AI guardrails
├── CLAUDE.md                  # Context memory for terminal agents
├── Dockerfile                 # Multi-stage production container build
├── .dockerignore              # Docker context exclusions
├── .gitignore                 # Git context exclusions
├── README.md                  # Master project release documentation
├── requirements.txt           # Python dependencies
├── run.py                     # Convenience runner script
├── app/                       # Backend application package
│   ├── __init__.py            # Package initializer
│   ├── main.py                # FastAPI application, REST endpoints, frontend mounts
│   └── schemas.py             # Pydantic v2 schemas, enums, tag normalization
├── frontend/                  # Frontend Kanban UI
│   ├── index.html             # Web UI HTML/CSS/JS dashboard
│   └── app.js                 # Client-side JavaScript logic
├── tests/                     # Unit test suite
│   ├── conftest.py            # Test configuration & path setup
│   └── test_main.py           # 43 automated unit tests
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow
└── docs/                      # Technical documentation & course deliverables
    ├── release-evidence.md    # Release verification & audit evidence
    ├── final-ai-review.md     # AI audit, tool comparison, and retrospective
    ├── ai-playbook.md         # Personal AI coding playbook & decision card
    ├── architecture.md        # System architecture synthesis & context log
    ├── midcourse/             # Mid-course sprint documentation
    │   ├── mini-adr.md        # Mid-course decision record
    │   ├── prompt-log.md      # AI prompt interaction log
    │   ├── reflection.md      # Mid-course reflection
    │   ├── user-stories.md    # User stories for due dates & tags
    │   └── verification.md    # Mid-course verification logs
    └── decisions/
        ├── in-memory-storage.md     # Task storage ADR
        └── comments-feature-plan.md # Comments extension plan
```

---

## 📌 Architectural Scope & Known Boundaries

- **In-Memory Storage**: Tasks are stored in memory using Python dictionaries (`_tasks`). State resets upon application restart. (See [docs/decisions/in-memory-storage.md](docs/decisions/in-memory-storage.md)).
- **Authentication**: User authentication is intentionally out of scope for this learning project.
- **CORS Configuration**: Permissive CORS (`allow_origins=["*"]`) enabled for local development.

---

## 📄 Documentation Directory Index

- [docs/release-evidence.md](docs/release-evidence.md): Consolidated release verification, test logs (43/43), CI fault injection proof, Docker security logs, break tests.
- [docs/final-ai-review.md](docs/final-ai-review.md): Consolidated AI review, security assessment, tool comparison matrix, governance retrospective.
- [docs/ai-playbook.md](docs/ai-playbook.md): Personal AI coding playbook, non-negotiable rules, decision checklist.
- [AGENTS.md](AGENTS.md): Repository instructions and AI coding guardrails.
- [CLAUDE.md](CLAUDE.md): Terminal agent operational memory.
- [docs/architecture.md](docs/architecture.md): Architecture overview and context engineering synthesis.
- [docs/decisions/in-memory-storage.md](docs/decisions/in-memory-storage.md): Technical decision record for task persistence.
- [docs/decisions/comments-feature-plan.md](docs/decisions/comments-feature-plan.md): Feature architectural critique for comments extension.
- [docs/midcourse/](docs/midcourse/): Mid-course sprint deliverables.
