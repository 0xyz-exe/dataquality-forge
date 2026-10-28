FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY dataquality_forge ./dataquality_forge

RUN pip install --no-cache-dir .

ENV ENV=production \
    STORAGE_DIR=/app/data/storage \
    REPORTS_DIR=/app/data/reports \
    DB_PATH=/app/data/dataquality.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

CMD ["uvicorn", "dataquality_forge.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
