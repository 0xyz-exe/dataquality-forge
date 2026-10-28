import time
import math
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from dataquality_forge.storage import load_dataset_dataframe
from dataquality_forge.rules.base import RULE_REGISTRY, RuleResult
import dataquality_forge.rules  # ensure rules are registered
from dataquality_forge.scoring import calculate_quality_score


def sanitize_row(row_dict: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in row_dict.items():
        if v is None or pd.isna(v):
            out[k] = None
        elif isinstance(v, (int, np.integer)):
            out[k] = int(v)
        elif isinstance(v, (float, np.floating)):
            out[k] = None if (math.isnan(v) or math.isinf(v)) else float(v)
        else:
            out[k] = str(v)
    return out


def execute_validation_run(
    file_path: str,
    rules: List[Dict[str, Any]],
    sample_limit: Optional[int] = None,
    max_failing_samples: int = 10,
) -> Dict[str, Any]:
    start_total = time.perf_counter()
    df = load_dataset_dataframe(file_path, limit=sample_limit)
    total_records = len(df)

    rule_results: List[Dict[str, Any]] = []
    passed_rules = 0
    failed_rules = 0
    warning_count = 0
    error_count = 0

    for r in rules:
        r_name = r.get("name", "Unnamed Rule")
        r_type = r.get("rule_type", "")
        cols = r.get("target_columns", [])
        params = r.get("parameters", {})
        severity = r.get("severity", "ERROR").upper()
        enabled = r.get("enabled", True)

        if not enabled:
            continue

        r_start = time.perf_counter()
        handler = RULE_REGISTRY.get(r_type)

        if not handler:
            res = RuleResult(
                rule_name=r_name,
                rule_type=r_type,
                target_columns=cols,
                severity=severity,
                total_records=total_records,
                passed_records=0,
                failed_records=total_records,
                pass_percentage=0.0,
                failure_percentage=100.0,
                duration_ms=0.0,
                passed=False,
                error_message=f"Unknown rule type: '{r_type}'",
            )
            failed_rules += 1
            if severity in ("ERROR", "CRITICAL"):
                error_count += 1
            else:
                warning_count += 1
            rule_results.append(res.to_dict())
            continue

        try:
            pass_mask, err_msg = handler(df, cols, params)
            r_dur = round((time.perf_counter() - r_start) * 1000, 2)

            passed_count = int(pass_mask.sum())
            failed_count = total_records - passed_count
            pass_pct = round((passed_count / total_records) * 100, 2) if total_records > 0 else 100.0
            fail_pct = round((failed_count / total_records) * 100, 2) if total_records > 0 else 0.0
            is_passed = (failed_count == 0) and (err_msg is None)

            # Sample failing rows
            failing_samples = []
            if failed_count > 0:
                failing_indices = df[~pass_mask].index[:max_failing_samples]
                failing_df = df.loc[failing_indices]
                failing_samples = [sanitize_row(row) for row in failing_df.to_dict(orient="records")]

            if is_passed:
                passed_rules += 1
            else:
                failed_rules += 1
                if severity in ("ERROR", "CRITICAL"):
                    error_count += 1
                else:
                    warning_count += 1

            res = RuleResult(
                rule_name=r_name,
                rule_type=r_type,
                target_columns=cols,
                severity=severity,
                total_records=total_records,
                passed_records=passed_count,
                failed_records=failed_count,
                pass_percentage=pass_pct,
                failure_percentage=fail_pct,
                duration_ms=r_dur,
                passed=is_passed,
                error_message=err_msg,
                sample_failing_rows=failing_samples,
            )
            rule_results.append(res.to_dict())

        except Exception as ex:
            r_dur = round((time.perf_counter() - r_start) * 1000, 2)
            failed_rules += 1
            error_count += 1
            res = RuleResult(
                rule_name=r_name,
                rule_type=r_type,
                target_columns=cols,
                severity=severity,
                total_records=total_records,
                passed_records=0,
                failed_records=total_records,
                pass_percentage=0.0,
                failure_percentage=100.0,
                duration_ms=r_dur,
                passed=False,
                error_message=f"Execution error: {str(ex)}",
            )
            rule_results.append(res.to_dict())

    duration_ms = round((time.perf_counter() - start_total) * 1000, 2)
    score_data = calculate_quality_score(rule_results)
    score = score_data.get("score") if score_data else None

    return {
        "status": "completed",
        "total_records": total_records,
        "rules_executed": len(rule_results),
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "warning_count": warning_count,
        "error_count": error_count,
        "quality_score": score,
        "score_breakdown": score_data,
        "duration_ms": duration_ms,
        "rule_results": rule_results,
    }
