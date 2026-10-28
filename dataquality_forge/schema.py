from typing import Dict, Any, List
import pandas as pd
from dataquality_forge.storage import load_dataset_dataframe


def extract_schema_from_dataframe(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    schema: Dict[str, Dict[str, Any]] = {}
    for col in df.columns:
        s = df[col]
        has_null = bool(s.isna().any())
        dtype_str = "string"
        if pd.api.types.is_bool_dtype(s):
            dtype_str = "boolean"
        elif pd.api.types.is_integer_dtype(s):
            dtype_str = "integer"
        elif pd.api.types.is_float_dtype(s):
            dtype_str = "float"
        elif pd.api.types.is_datetime64_any_dtype(s):
            dtype_str = "datetime"

        schema[str(col)] = {
            "type": dtype_str,
            "nullable": has_null,
            "required": not has_null,
        }
    return schema


def extract_schema_from_file(file_path: str) -> Dict[str, Dict[str, Any]]:
    df = load_dataset_dataframe(file_path, limit=200)
    return extract_schema_from_dataframe(df)


def compare_schemas(
    expected_schema: Dict[str, Dict[str, Any]],
    actual_schema: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    expected_cols = set(expected_schema.keys())
    actual_cols = set(actual_schema.keys())

    missing_columns = sorted(list(expected_cols - actual_cols))
    added_columns = sorted(list(actual_cols - expected_cols))
    common_columns = expected_cols.intersection(actual_cols)

    type_changes = []
    nullability_changes = []
    breaking_changes = []

    for col in missing_columns:
        breaking_changes.append(f"Required column '{col}' is missing in actual schema.")

    for col in common_columns:
        exp_info = expected_schema[col]
        act_info = actual_schema[col]

        exp_type = exp_info.get("type", "string").lower()
        act_type = act_info.get("type", "string").lower()
        if exp_type != act_type:
            change_msg = f"Column '{col}' type changed from '{exp_type}' to '{act_type}'."
            type_changes.append({
                "column": col,
                "expected_type": exp_type,
                "actual_type": act_type,
            })
            breaking_changes.append(change_msg)

        exp_nullable = exp_info.get("nullable", True)
        act_nullable = act_info.get("nullable", False)
        if not exp_nullable and act_nullable:
            change_msg = f"Column '{col}' is non-nullable in expected schema but contains null values in actual dataset."
            nullability_changes.append({
                "column": col,
                "expected_nullable": exp_nullable,
                "actual_nullable": act_nullable,
            })
            breaking_changes.append(change_msg)

    is_compatible = len(breaking_changes) == 0

    return {
        "is_compatible": is_compatible,
        "breaking_changes": breaking_changes,
        "missing_columns": missing_columns,
        "added_columns": added_columns,
        "type_changes": type_changes,
        "nullability_changes": nullability_changes,
        "summary": "Schema is fully compatible." if is_compatible else f"Found {len(breaking_changes)} breaking schema changes.",
    }
