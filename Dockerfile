# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install into a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Stage 2: Final production image
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Create a non-root system user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false app

WORKDIR /app

# Copy virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source code, app package, and frontend files
COPY app/ /app/app/
COPY frontend/ /app/frontend/
COPY run.py /app/

# Set appropriate directory ownership for non-root user
RUN chown -R app:appgroup /app

# Switch to non-root user before running container process
USER app

EXPOSE 8000

# Container healthcheck against endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start FastAPI server using Uvicorn without reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
