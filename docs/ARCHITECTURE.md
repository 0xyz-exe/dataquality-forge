# Architecture & System Design

DataQuality Forge is structured as an open-source data quality profiling and assertion platform designed for local self-hosting, developer sandboxes, and CI/CD automated gates.

## System Topography

```
                    ┌─────────────────────────┐
                    │   React 19 + Tailwind   │
                    │   Vite SPA Dashboard    │
                    └────────────┬────────────┘
                                 │ HTTP / REST
                    ┌────────────▼────────────┐
                    │      FastAPI / v1       │
                    │   API & Job Runner      │
                    └─────┬──────┬──────┬─────┘
                          │      │      │
          ┌───────────────┘      │      └───────────────┐
          │                      │                      │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│  Profiling Engine │  │ Validation Engine │  │  Schema Engine    │
│  DuckDB + Pandas  │  │ 10 Rule Families  │  │  Diff & Evolution │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          └───────────────┬──────┴──────────────────────┘
                          │
                ┌─────────▼─────────┐
                │ SQLite / Postgres │
                │ Metadata Storage  │
                └───────────────────┘
```

## Key Subsystems

1. **Storage Sandbox**: Isolated file repository with checksum calculation, MIME validation, and path traversal protection.
2. **Profiling Engine**: DuckDB-accelerated summary statistics, duplicate detection, missing rates, and quantile analysis.
3. **Validation Rules Engine**: Predefined declarative rules across 10 functional families. Never relies on arbitrary code `eval()`.
4. **Scoring Engine**: Severity-weighted calculation normalizing rule results to an explainable 0-100% index.
5. **CLI Client**: Headless command-line utility for local script execution and pipeline gating with standard exit codes (0, 1, 2, 3).
