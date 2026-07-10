# --- InterviewPilot backend ---
FROM python:3.12-slim

# node is needed so the code runner can execute JavaScript submissions
RUN apt-get update && apt-get install -y --no-install-recommends nodejs curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt "psycopg[binary]>=3.2"

COPY app ./app

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8002
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:8002/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
