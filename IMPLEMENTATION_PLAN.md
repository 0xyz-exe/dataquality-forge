# DataQuality Forge — Implementation Plan

## Phase 1: Foundation & Plan
- Repo inspection, directory structure, `.gitignore`, license (MIT), `IMPLEMENTATION_PLAN.md`, `TASKS.md`.

## Phase 2: Python Backend & Core Engines
- Virtual environment setup with `uv`.
- Core dependencies: `fastapi`, `uvicorn`, `duckdb`, `pandas`, `pyarrow`, `pydantic`, `sqlalchemy`, `typer`, `pytest`, `pytest-asyncio`, `httpx`, `python-multipart`.
- Storage & Ingestion service: CSV, JSON, JSON Lines, Parquet parsers with boundary limits and sanitization.
- Profiling Engine: exact & sampling profiling, dataset metrics (row/col counts, duplicate rows, missing rate), column metrics (types, nulls, distincts, quantiles, distributions).
- Validation Rules Engine: 10 rule classes (Completeness, Uniqueness, Type, Range, Pattern, Categorical, Referential, Date, Cross-column, Statistical IQR/Z-score).
- Scoring Engine: transparent weighted formula, explainable score breakdown.
- Schema Registry & Change Detection: type comparison, column addition/removal/rename.
- Reporting Service: JSON, CSV, HTML export.
- CLI: `dataquality` commands.

## Phase 3: REST API & Storage Persistence
- FastAPI application (`/api/v1/...`).
- SQLite persistence for local/dev, Postgres compatible.
- Health endpoints (`/health/live`, `/health/ready`).
- Audit & run history tracking.

## Phase 4: Frontend Web Application
- Next.js App Router (TypeScript, Tailwind CSS, Lucide React).
- Dashboard overview, Project/Dataset management, Data preview, Profiling visualizer, Rule builder, Validation runner & results, Schema inspector, Report exporter.

## Phase 5: Testing & Verification
- Unit & integration tests via pytest.
- End-to-end testing with Playwright / browser automation.
- Edge case handling.

## Phase 6: Documentation, Deployment & GitHub Publication
- Dockerfile & docker-compose.yml.
- Synthetic datasets in `examples/`.
- Docs suite (`docs/*.md`, `README.md`).
- Live screenshot capture.
- GitHub repo creation (`0xyz-exe/dataquality-forge`, public), commit, push.
