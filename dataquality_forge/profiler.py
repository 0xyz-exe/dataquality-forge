import time
import math
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from dataquality_forge.storage import load_dataset_dataframe


def sanitize_val(val: Any) -> Any:
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        if math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return str(val)
    return str(val)


def profile_dataset(file_path: str, sample_limit: Optional[int] = None) -> Dict[str, Any]:
    start_time = time.perf_counter()
    df = load_dataset_dataframe(file_path, limit=sample_limit)

    total_rows = int(len(df))
    total_cols = int(len(df.columns))
    mode = "sampling" if sample_limit and total_rows == sample_limit else "exact"

    if total_rows == 0:
        return {
            "mode": mode,
            "sample_size": sample_limit,
            "duration_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "total_rows": 0,
            "total_columns": total_cols,
            "duplicate_rows": 0,
            "duplicate_row_percentage": 0.0,
            "missing_cells": 0,
            "missing_cell_percentage": 0.0,
            "complete_rows": 0,
            "complete_row_percentage": 0.0,
            "column_type_distribution": {},
            "column_profiles": [],
            "summary_text": "Empty dataset with 0 rows."
        }

    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_rows / total_rows) * 100, 2)

    # Missing cells & complete rows
    null_matrix = df.isna()
    missing_cells = int(null_matrix.sum().sum())
    total_cells = total_rows * total_cols
    missing_cell_pct = round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0
    complete_rows = int((~null_matrix.any(axis=1)).sum())
    complete_row_pct = round((complete_rows / total_rows) * 100, 2)

    col_profiles = []
    type_counts: Dict[str, int] = {}

    for col in df.columns:
        s = df[col]
        col_nulls = int(s.isna().sum())
        col_non_nulls = total_rows - col_nulls
        null_pct = round((col_nulls / total_rows) * 100, 2)
        valid_s = s.dropna()

        # Type inference
        inferred_type = "string"
        if pd.api.types.is_bool_dtype(s):
            inferred_type = "boolean"
        elif pd.api.types.is_integer_dtype(s):
            inferred_type = "integer"
        elif pd.api.types.is_float_dtype(s):
            inferred_type = "float"
        elif pd.api.types.is_datetime64_any_dtype(s):
            inferred_type = "datetime"
        else:
            # Check if strings can be parsed as dates or numbers
            sample_non_null = valid_s.head(100)
            if not sample_non_null.empty:
                numeric_try = pd.to_numeric(sample_non_null, errors="coerce")
                if numeric_try.notna().all():
                    inferred_type = "integer" if (numeric_try % 1 == 0).all() else "float"
                else:
                    date_try = pd.to_datetime(sample_non_null, errors="coerce", format="mixed")
                    if date_try.notna().all() and sample_non_null.astype(str).str.contains(r"[-/:]").all():
                        inferred_type = "datetime"

        type_counts[inferred_type] = type_counts.get(inferred_type, 0) + 1

        # Distincts
        distinct_count = int(valid_s.nunique())
        distinct_pct = round((distinct_count / total_rows) * 100, 2)

        # Top frequent values
        top_val_counts = valid_s.value_counts().head(10)
        top_values = [
            {"value": sanitize_val(idx), "count": int(cnt), "percentage": round((cnt / total_rows) * 100, 2)}
            for idx, cnt in top_val_counts.items()
        ]

        # Samples
        samples = [sanitize_val(v) for v in valid_s.head(5).tolist()]

        col_stat: Dict[str, Any] = {
            "name": str(col),
            "inferred_type": inferred_type,
            "null_count": col_nulls,
            "null_percentage": null_pct,
            "non_null_count": col_non_nulls,
            "distinct_count": distinct_count,
            "distinct_percentage": distinct_pct,
            "top_values": top_values,
            "sample_values": samples,
            "empty_string_count": 0,
            "whitespace_count": 0,
            "numeric_stats": None,
            "datetime_stats": None,
            "boolean_stats": None,
        }

        # String specific stats
        if inferred_type == "string":
            str_s = valid_s.astype(str)
            col_stat["empty_string_count"] = int((str_s == "").sum())
            col_stat["whitespace_count"] = int((str_s.str.strip() == "").sum() - col_stat["empty_string_count"])
            str_lengths = str_s.str.len()
            col_stat["min_length"] = int(str_lengths.min()) if not str_lengths.empty else 0
            col_stat["max_length"] = int(str_lengths.max()) if not str_lengths.empty else 0
            col_stat["avg_length"] = round(float(str_lengths.mean()), 2) if not str_lengths.empty else 0.0

        # Numeric stats
        elif inferred_type in ("integer", "float"):
            num_s = pd.to_numeric(valid_s, errors="coerce").dropna()
            if not num_s.empty:
                col_stat["numeric_stats"] = {
                    "min": sanitize_val(num_s.min()),
                    "max": sanitize_val(num_s.max()),
                    "mean": sanitize_val(round(float(num_s.mean()), 4)),
                    "median": sanitize_val(round(float(num_s.median()), 4)),
                    "std": sanitize_val(round(float(num_s.std(ddof=0)), 4)) if len(num_s) > 1 else 0.0,
                    "q25": sanitize_val(round(float(num_s.quantile(0.25)), 4)),
                    "q50": sanitize_val(round(float(num_s.quantile(0.50)), 4)),
                    "q75": sanitize_val(round(float(num_s.quantile(0.75)), 4)),
                }

        # Datetime stats
        elif inferred_type == "datetime":
            dt_s = pd.to_datetime(valid_s, errors="coerce", format="mixed").dropna()
            if not dt_s.empty:
                col_stat["datetime_stats"] = {
                    "min": str(dt_s.min()),
                    "max": str(dt_s.max()),
                    "range_days": round((dt_s.max() - dt_s.min()).total_seconds() / 86400, 2),
                }

        # Boolean stats
        elif inferred_type == "boolean":
            b_s = valid_s.astype(bool)
            col_stat["boolean_stats"] = {
                "true_count": int(b_s.sum()),
                "false_count": int((~b_s).sum()),
            }

        col_profiles.append(col_stat)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    summary_text = (
        f"Analyzed {total_rows} rows and {total_cols} columns in {duration_ms}ms. "
        f"Found {duplicate_rows} duplicate rows ({duplicate_pct}%) and "
        f"{missing_cells} missing cells ({missing_cell_pct}%)."
    )

    return {
        "mode": mode,
        "sample_size": sample_limit,
        "duration_ms": duration_ms,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "duplicate_row_percentage": duplicate_pct,
        "missing_cells": missing_cells,
        "missing_cell_percentage": missing_cell_pct,
        "complete_rows": complete_rows,
        "complete_row_percentage": complete_row_pct,
        "column_type_distribution": type_counts,
        "column_profiles": col_profiles,
        "summary_text": summary_text,
    }
