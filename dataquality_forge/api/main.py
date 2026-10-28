import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from dataquality_forge import __version__
from dataquality_forge.database import get_db, init_db
from dataquality_forge.config import ALLOWED_EXTENSIONS, STORAGE_DIR
from dataquality_forge.models import (
    Project,
    Dataset,
    ProfilingRun,
    ValidationRule,
    ValidationRun,
    ExpectedSchema,
)
from dataquality_forge.storage import (
    save_upload_file,
    load_dataset_dataframe,
    StorageError,
)
from dataquality_forge.profiler import profile_dataset, sanitize_val
from dataquality_forge.validator import execute_validation_run
from dataquality_forge.schema import (
    extract_schema_from_dataframe,
    compare_schemas,
)
from dataquality_forge.reports import (
    generate_json_report,
    generate_csv_report,
    generate_html_report,
)

init_db()

app = FastAPI(
    title="DataQuality Forge API",
    version=__version__,
    description="Open-Source Data Quality Profiling & Validation Platform API",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for dev/production local usage
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Health Endpoints ----------------
@app.get("/health/live")
def health_live():
    return {"status": "ok", "version": __version__}


@app.get("/health/ready")
def health_ready(db: Session = Depends(get_db)):
    # Database check
    try:
        db.execute(Project.__table__.select().limit(1))
        db_ok = True
    except Exception:
        db_ok = False

    storage_ok = STORAGE_DIR.exists() and os.access(STORAGE_DIR, os.W_OK)
    ready = db_ok and storage_ok
    status_code = 200 if ready else 503
    return Response(
        content=f'{{"status":"{"ready" if ready else "unready"}","database":{str(db_ok).lower()},"storage":{str(storage_ok).lower()}}}',
        media_type="application/json",
        status_code=status_code,
    )


# ---------------- Schemas ----------------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str
    target_columns: List[str]
    parameters: Dict[str, Any] = {}
    severity: str = "ERROR"
    enabled: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    severity: Optional[str] = None
    enabled: Optional[bool] = None


class ExpectedSchemaCreate(BaseModel):
    name: str = "Default Expected Schema"
    columns: Dict[str, Dict[str, Any]]


# ---------------- Dashboard Overview ----------------
@app.get("/api/v1/overview")
def get_overview(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    total_datasets = db.query(Dataset).count()
    total_runs = db.query(ValidationRun).count()

    runs = db.query(ValidationRun).all()
    scores = [r.quality_score for r in runs if r.quality_score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    recent_runs = [
        {
            "id": r.id,
            "dataset_id": r.dataset_id,
            "status": r.status,
            "quality_score": r.quality_score,
            "rules_executed": r.rules_executed,
            "passed_rules": r.passed_rules,
            "failed_rules": r.failed_rules,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in db.query(ValidationRun).order_by(ValidationRun.created_at.desc()).limit(5).all()
    ]

    recent_datasets = [
        {
            "id": d.id,
            "name": d.name,
            "row_count": d.row_count,
            "column_count": d.column_count,
            "file_format": d.file_format,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in db.query(Dataset).order_by(Dataset.created_at.desc()).limit(5).all()
    ]

    return {
        "total_projects": total_projects,
        "total_datasets": total_datasets,
        "total_validation_runs": total_runs,
        "average_quality_score": avg_score,
        "recent_runs": recent_runs,
        "recent_datasets": recent_datasets,
    }


# ---------------- Projects ----------------
@app.get("/api/v1/projects")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "dataset_count": len(p.datasets),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in projects
    ]


@app.post("/api/v1/projects")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Project).filter(Project.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project name already exists")
    p = Project(name=data.name, description=data.description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name, "description": p.description}


@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "datasets": [
            {
                "id": d.id,
                "name": d.name,
                "file_format": d.file_format,
                "row_count": d.row_count,
                "column_count": d.column_count,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in p.datasets
        ],
    }


@app.delete("/api/v1/projects/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    db.commit()
    return {"status": "deleted", "id": project_id}


# ---------------- Datasets ----------------
@app.get("/api/v1/datasets")
def list_datasets(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Dataset)
    if project_id:
        q = q.filter(Dataset.project_id == project_id)
    datasets = q.order_by(Dataset.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "project_id": d.project_id,
            "name": d.name,
            "description": d.description,
            "original_filename": d.original_filename,
            "file_format": d.file_format,
            "file_size_bytes": d.file_size_bytes,
            "row_count": d.row_count,
            "column_count": d.column_count,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in datasets
    ]


@app.post("/api/v1/datasets")
async def upload_dataset(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    content = await file.read()
    try:
        dest_path, fmt, checksum, size = save_upload_file(content, file.filename or "data.csv")
        df_head = load_dataset_dataframe(str(dest_path), limit=100)
        schema_meta = extract_schema_from_dataframe(df_head)

        # Full row count inference
        full_df = load_dataset_dataframe(str(dest_path))
        row_count = len(full_df)
        col_count = len(full_df.columns)

        ds = Dataset(
            project_id=project_id,
            name=name or file.filename or "Untitled Dataset",
            description=description,
            original_filename=file.filename or "data.csv",
            file_format=fmt,
            file_size_bytes=size,
            file_path=str(dest_path),
            file_checksum=checksum,
            row_count=row_count,
            column_count=col_count,
            schema_metadata=schema_meta,
            status="ready",
        )
        db.add(ds)
        db.commit()
        db.refresh(ds)
        return {
            "id": ds.id,
            "name": ds.name,
            "file_format": ds.file_format,
            "row_count": ds.row_count,
            "column_count": ds.column_count,
            "status": ds.status,
        }
    except StorageError as se:
        raise HTTPException(status_code=400, detail=str(se))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process dataset: {str(e)}")


@app.get("/api/v1/datasets/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {
        "id": d.id,
        "project_id": d.project_id,
        "name": d.name,
        "description": d.description,
        "original_filename": d.original_filename,
        "file_format": d.file_format,
        "file_size_bytes": d.file_size_bytes,
        "row_count": d.row_count,
        "column_count": d.column_count,
        "status": d.status,
        "file_checksum": d.file_checksum,
        "schema_metadata": d.schema_metadata,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


@app.delete("/api/v1/datasets/{dataset_id}")
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    # Clean up file on disk
    try:
        p = Path(d.file_path)
        if p.exists():
            p.unlink()
    except Exception:
        pass
    db.delete(d)
    db.commit()
    return {"status": "deleted", "id": dataset_id}


@app.get("/api/v1/datasets/{dataset_id}/preview")
def preview_dataset(dataset_id: str, limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        df = load_dataset_dataframe(d.file_path, limit=limit)
        clean_rows = []
        for r in df.to_dict(orient="records"):
            clean_rows.append({k: sanitize_val(v) for k, v in r.items()})
        return {
            "columns": list(df.columns),
            "rows": clean_rows,
            "total_previewed": len(clean_rows),
            "total_rows": d.row_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


# ---------------- Profiling ----------------
@app.post("/api/v1/datasets/{dataset_id}/profile")
def run_profile(dataset_id: str, sample_limit: Optional[int] = Query(None), db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        prof = profile_dataset(d.file_path, sample_limit=sample_limit)
        pr = ProfilingRun(
            dataset_id=dataset_id,
            status="completed",
            mode=prof["mode"],
            sample_size=prof.get("sample_size"),
            duration_ms=prof["duration_ms"],
            total_rows=prof["total_rows"],
            total_columns=prof["total_columns"],
            duplicate_rows=prof["duplicate_rows"],
            duplicate_row_percentage=prof["duplicate_row_percentage"],
            missing_cells=prof["missing_cells"],
            missing_cell_percentage=prof["missing_cell_percentage"],
            complete_rows=prof["complete_rows"],
            complete_row_percentage=prof["complete_row_percentage"],
            column_type_distribution=prof["column_type_distribution"],
            column_profiles=prof["column_profiles"],
            summary_text=prof["summary_text"],
        )
        db.add(pr)
        db.commit()
        db.refresh(pr)
        return {
            "run_id": pr.id,
            "summary": prof,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profiling failed: {str(e)}")


@app.get("/api/v1/datasets/{dataset_id}/profile")
def get_latest_profile(dataset_id: str, db: Session = Depends(get_db)):
    pr = (
        db.query(ProfilingRun)
        .filter(ProfilingRun.dataset_id == dataset_id)
        .order_by(ProfilingRun.created_at.desc())
        .first()
    )
    if not pr:
        raise HTTPException(status_code=404, detail="No profiling run found for dataset")
    return {
        "id": pr.id,
        "mode": pr.mode,
        "duration_ms": pr.duration_ms,
        "total_rows": pr.total_rows,
        "total_columns": pr.total_columns,
        "duplicate_rows": pr.duplicate_rows,
        "duplicate_row_percentage": pr.duplicate_row_percentage,
        "missing_cells": pr.missing_cells,
        "missing_cell_percentage": pr.missing_cell_percentage,
        "complete_rows": pr.complete_rows,
        "complete_row_percentage": pr.complete_row_percentage,
        "column_type_distribution": pr.column_type_distribution,
        "column_profiles": pr.column_profiles,
        "summary_text": pr.summary_text,
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
    }


# ---------------- Rules ----------------
@app.get("/api/v1/datasets/{dataset_id}/rules")
def list_rules(dataset_id: str, db: Session = Depends(get_db)):
    rules = db.query(ValidationRule).filter(ValidationRule.dataset_id == dataset_id).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "rule_type": r.rule_type,
            "target_columns": r.target_columns,
            "parameters": r.parameters,
            "severity": r.severity,
            "enabled": r.enabled,
            "version": r.version,
        }
        for r in rules
    ]


@app.post("/api/v1/datasets/{dataset_id}/rules")
def create_rule(dataset_id: str, data: RuleCreate, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    rule = ValidationRule(
        dataset_id=dataset_id,
        name=data.name,
        description=data.description,
        rule_type=data.rule_type,
        target_columns=data.target_columns,
        parameters=data.parameters,
        severity=data.severity,
        enabled=data.enabled,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "name": rule.name, "rule_type": rule.rule_type}


@app.patch("/api/v1/rules/{rule_id}")
def update_rule(rule_id: str, data: RuleUpdate, db: Session = Depends(get_db)):
    r = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rule not found")
    if data.name is not None:
        r.name = data.name
    if data.description is not None:
        r.description = data.description
    if data.parameters is not None:
        r.parameters = data.parameters
    if data.severity is not None:
        r.severity = data.severity
    if data.enabled is not None:
        r.enabled = data.enabled
    r.version += 1
    db.commit()
    return {"id": r.id, "status": "updated", "version": r.version}


@app.delete("/api/v1/rules/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    r = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(r)
    db.commit()
    return {"status": "deleted", "id": rule_id}


# ---------------- Validation Runs ----------------
@app.post("/api/v1/datasets/{dataset_id}/validation-runs")
def run_validation(dataset_id: str, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    rules = db.query(ValidationRule).filter(ValidationRule.dataset_id == dataset_id, ValidationRule.enabled == True).all()
    rule_dicts = [
        {
            "name": r.name,
            "rule_type": r.rule_type,
            "target_columns": r.target_columns,
            "parameters": r.parameters,
            "severity": r.severity,
            "enabled": r.enabled,
        }
        for r in rules
    ]

    result = execute_validation_run(d.file_path, rule_dicts)
    vr = ValidationRun(
        dataset_id=dataset_id,
        status="completed",
        rules_executed=result["rules_executed"],
        passed_rules=result["passed_rules"],
        failed_rules=result["failed_rules"],
        warning_count=result["warning_count"],
        error_count=result["error_count"],
        quality_score=result["quality_score"],
        duration_ms=result["duration_ms"],
        score_breakdown=result["score_breakdown"],
        rule_results=result["rule_results"],
    )
    db.add(vr)
    db.commit()
    db.refresh(vr)
    return {
        "run_id": vr.id,
        "quality_score": vr.quality_score,
        "rules_executed": vr.rules_executed,
        "passed_rules": vr.passed_rules,
        "failed_rules": vr.failed_rules,
        "duration_ms": vr.duration_ms,
        "rule_results": vr.rule_results,
    }


@app.get("/api/v1/validation-runs")
def list_validation_runs(dataset_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(ValidationRun)
    if dataset_id:
        q = q.filter(ValidationRun.dataset_id == dataset_id)
    runs = q.order_by(ValidationRun.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "dataset_id": r.dataset_id,
            "status": r.status,
            "quality_score": r.quality_score,
            "rules_executed": r.rules_executed,
            "passed_rules": r.passed_rules,
            "failed_rules": r.failed_rules,
            "duration_ms": r.duration_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]


@app.get("/api/v1/validation-runs/{run_id}")
def get_validation_run(run_id: str, db: Session = Depends(get_db)):
    vr = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
    if not vr:
        raise HTTPException(status_code=404, detail="Validation run not found")
    return {
        "id": vr.id,
        "dataset_id": vr.dataset_id,
        "status": vr.status,
        "quality_score": vr.quality_score,
        "rules_executed": vr.rules_executed,
        "passed_rules": vr.passed_rules,
        "failed_rules": vr.failed_rules,
        "warning_count": vr.warning_count,
        "error_count": vr.error_count,
        "duration_ms": vr.duration_ms,
        "score_breakdown": vr.score_breakdown,
        "rule_results": vr.rule_results,
        "created_at": vr.created_at.isoformat() if vr.created_at else None,
    }


@app.get("/api/v1/validation-runs/{run_id}/report")
def export_report(run_id: str, format: str = Query("json", pattern="^(json|csv|html)$"), db: Session = Depends(get_db)):
    vr = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
    if not vr:
        raise HTTPException(status_code=404, detail="Validation run not found")
    dataset = db.query(Dataset).filter(Dataset.id == vr.dataset_id).first()
    ds_name = dataset.name if dataset else "Dataset"

    val_data = {
        "validation_run_id": vr.id,
        "dataset_id": vr.dataset_id,
        "dataset_name": ds_name,
        "quality_score": vr.quality_score,
        "total_records": dataset.row_count if dataset else 0,
        "rules_executed": vr.rules_executed,
        "passed_rules": vr.passed_rules,
        "failed_rules": vr.failed_rules,
        "duration_ms": vr.duration_ms,
        "score_breakdown": vr.score_breakdown,
        "rule_results": vr.rule_results,
    }

    if format == "json":
        return Response(content=generate_json_report(val_data), media_type="application/json")
    elif format == "csv":
        return Response(
            content=generate_csv_report(val_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{run_id}.csv"},
        )
    elif format == "html":
        return Response(content=generate_html_report(val_data, dataset_name=ds_name), media_type="text/html")


# ---------------- Schema Comparison ----------------
@app.post("/api/v1/datasets/{dataset_id}/expected-schema")
def save_expected_schema(dataset_id: str, data: ExpectedSchemaCreate, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    es = ExpectedSchema(dataset_id=dataset_id, name=data.name, columns=data.columns)
    db.add(es)
    db.commit()
    db.refresh(es)
    return {"id": es.id, "name": es.name}


@app.get("/api/v1/datasets/{dataset_id}/schema-diff")
def diff_schema(dataset_id: str, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    es = db.query(ExpectedSchema).filter(ExpectedSchema.dataset_id == dataset_id).order_by(ExpectedSchema.created_at.desc()).first()
    if not es:
        return {"has_expected_schema": False, "message": "No expected schema registered for this dataset"}
    actual_schema = d.schema_metadata or extract_schema_from_dataframe(load_dataset_dataframe(d.file_path, limit=100))
    diff = compare_schemas(es.columns, actual_schema)
    return {
        "has_expected_schema": True,
        "expected_schema": es.columns,
        "actual_schema": actual_schema,
        "diff": diff,
    }
