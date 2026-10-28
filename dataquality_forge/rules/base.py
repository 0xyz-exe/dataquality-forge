import re
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
import pandas as pd
import numpy as np


class RuleResult:
    def __init__(
        self,
        rule_name: str,
        rule_type: str,
        target_columns: List[str],
        severity: str,
        total_records: int,
        passed_records: int,
        failed_records: int,
        pass_percentage: float,
        failure_percentage: float,
        duration_ms: float,
        passed: bool,
        error_message: Optional[str] = None,
        sample_failing_rows: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.rule_name = rule_name
        self.rule_type = rule_type
        self.target_columns = target_columns
        self.severity = severity
        self.total_records = total_records
        self.passed_records = passed_records
        self.failed_records = failed_records
        self.pass_percentage = pass_percentage
        self.failure_percentage = failure_percentage
        self.duration_ms = duration_ms
        self.passed = passed
        self.error_message = error_message
        self.sample_failing_rows = sample_failing_rows or []
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "rule_type": self.rule_type,
            "target_columns": self.target_columns,
            "severity": self.severity,
            "total_records": self.total_records,
            "passed_records": self.passed_records,
            "failed_records": self.failed_records,
            "pass_percentage": self.pass_percentage,
            "failure_percentage": self.failure_percentage,
            "duration_ms": self.duration_ms,
            "passed": self.passed,
            "error_message": self.error_message,
            "sample_failing_rows": self.sample_failing_rows,
            "details": self.details,
        }


# Global Rule Registry: rule_type -> callable(df, target_columns, params) -> Tuple[bool, int, int, pd.Series, Optional[str]]
RULE_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_rule(rule_type: str):
    def decorator(fn: Callable[..., Any]):
        RULE_REGISTRY[rule_type] = fn
        return fn
    return decorator
