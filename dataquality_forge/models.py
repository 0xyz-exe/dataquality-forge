import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from dataquality_forge.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    original_filename = Column(String(255), nullable=False)
    file_format = Column(String(20), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    file_checksum = Column(String(64), nullable=False)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    status = Column(String(30), default="ready")  # ready, processing, failed
    schema_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    project = relationship("Project", back_populates="datasets")
    profiling_runs = relationship("ProfilingRun", back_populates="dataset", cascade="all, delete-orphan")
    rules = relationship("ValidationRule", back_populates="dataset", cascade="all, delete-orphan")
    validation_runs = relationship("ValidationRun", back_populates="dataset", cascade="all, delete-orphan")
    expected_schemas = relationship("ExpectedSchema", back_populates="dataset", cascade="all, delete-orphan")


class ProfilingRun(Base):
    __tablename__ = "profiling_runs"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    status = Column(String(30), default="completed")
    mode = Column(String(20), default="exact")  # exact, sampling
    sample_size = Column(Integer, nullable=True)
    duration_ms = Column(Float, nullable=False)
    total_rows = Column(Integer, nullable=False)
    total_columns = Column(Integer, nullable=False)
    duplicate_rows = Column(Integer, nullable=False)
    duplicate_row_percentage = Column(Float, nullable=False)
    missing_cells = Column(Integer, nullable=False)
    missing_cell_percentage = Column(Float, nullable=False)
    complete_rows = Column(Integer, nullable=False)
    complete_row_percentage = Column(Float, nullable=False)
    column_type_distribution = Column(JSON, nullable=True)
    column_profiles = Column(JSON, nullable=False)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    dataset = relationship("Dataset", back_populates="profiling_runs")


class ValidationRule(Base):
    __tablename__ = "validation_rules"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False)
    target_columns = Column(JSON, nullable=False)  # list of str
    parameters = Column(JSON, nullable=False, default=dict)
    severity = Column(String(20), default="ERROR")  # INFO, WARNING, ERROR, CRITICAL
    enabled = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    dataset = relationship("Dataset", back_populates="rules")


class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    status = Column(String(30), default="completed")  # pending, running, completed, failed
    rules_executed = Column(Integer, default=0)
    passed_rules = Column(Integer, default=0)
    failed_rules = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    quality_score = Column(Float, nullable=True)
    duration_ms = Column(Float, default=0.0)
    score_breakdown = Column(JSON, nullable=True)
    rule_results = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    dataset = relationship("Dataset", back_populates="validation_runs")


class ExpectedSchema(Base):
    __tablename__ = "expected_schemas"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    name = Column(String(120), nullable=False)
    columns = Column(JSON, nullable=False)  # dict: {col_name: {type: str, nullable: bool, required: bool}}
    created_at = Column(DateTime, default=utcnow)

    dataset = relationship("Dataset", back_populates="expected_schemas")
