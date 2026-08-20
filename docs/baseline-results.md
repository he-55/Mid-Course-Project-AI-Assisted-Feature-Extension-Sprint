# Baseline Results

The original feature-extension baseline had 43 tests. After the final package-layout refactor and the description-clear correction, the current verification command is:

```text
.venv/bin/python -m pytest -v
47 passed, 1 warning in 0.21s
```

The warning is Starlette's deprecation warning for the installed TestClient/httpx combination; it does not fail the suite.
