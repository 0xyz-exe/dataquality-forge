import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from dataquality_forge.rules.base import register_rule

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# ---------------- Completeness ----------------
@register_rule("not_null")
def check_not_null(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    return df[col].notna(), None


@register_rule("max_null_percentage")
def check_max_null_pct(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    max_pct = float(params.get("max_percentage", 0.0))
    null_pct = (df[col].isna().sum() / len(df)) * 100 if len(df) > 0 else 0.0
    passed = null_pct <= max_pct
    return pd.Series(passed, index=df.index), f"Null percentage {null_pct:.2f}% exceeds threshold {max_pct}%" if not passed else None


@register_rule("not_empty_string")
def check_not_empty(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    s = df[col].fillna("")
    return s.astype(str) != "", None


@register_rule("not_whitespace")
def check_not_whitespace(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    s = df[col].fillna("").astype(str).str.strip()
    return s != "", None


# ---------------- Uniqueness ----------------
@register_rule("unique_column")
def check_unique(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    # Mark duplicates as False
    return ~df.duplicated(subset=[col], keep=False), None


@register_rule("unique_composite")
def check_unique_composite(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    missing = [c for c in target_columns if c not in df.columns]
    if missing:
        return pd.Series(False, index=df.index), f"Columns {missing} not in dataset"
    return ~df.duplicated(subset=target_columns, keep=False), None


@register_rule("no_duplicate_rows")
def check_no_duplicate_rows(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    return ~df.duplicated(keep=False), None


# ---------------- Type Rules ----------------
@register_rule("is_type")
def check_is_type(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    expected = params.get("expected_type", "string").lower()
    s = df[col].dropna()

    if expected in ("int", "integer"):
        mask = s.map(lambda v: isinstance(v, (int, np.integer)) or (isinstance(v, float) and v.is_integer()))
    elif expected in ("float", "numeric", "number"):
        mask = s.map(lambda v: isinstance(v, (int, float, np.number)))
    elif expected in ("bool", "boolean"):
        mask = s.map(lambda v: isinstance(v, (bool, np.bool_)))
    elif expected in ("str", "string"):
        mask = s.map(lambda v: isinstance(v, str))
    elif expected in ("date", "datetime"):
        mask = pd.to_datetime(s, errors="coerce", format="mixed").notna()
    else:
        mask = pd.Series(True, index=s.index)

    full_mask = pd.Series(True, index=df.index)
    full_mask.loc[s.index] = mask
    return full_mask, None


# ---------------- Range Rules ----------------
@register_rule("min_value")
def check_min_value(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    min_val = float(params.get("min_value", 0))
    num_s = pd.to_numeric(df[col], errors="coerce")
    return num_s >= min_val, None


@register_rule("max_value")
def check_max_value(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    max_val = float(params.get("max_value", 0))
    num_s = pd.to_numeric(df[col], errors="coerce")
    return num_s <= max_val, None


@register_rule("value_between")
def check_value_between(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    min_v = float(params.get("min_value", float("-inf")))
    max_v = float(params.get("max_value", float("inf")))
    inclusive = bool(params.get("inclusive", True))
    num_s = pd.to_numeric(df[col], errors="coerce")
    if inclusive:
        return (num_s >= min_v) & (num_s <= max_v), None
    return (num_s > min_v) & (num_s < max_v), None


@register_rule("string_length_between")
def check_str_len(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    min_l = int(params.get("min_length", 0))
    max_l = int(params.get("max_length", 999999))
    lengths = df[col].fillna("").astype(str).str.len()
    return (lengths >= min_l) & (lengths <= max_l), None


# ---------------- Pattern Rules ----------------
@register_rule("regex_match")
def check_regex(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    pattern = params.get("pattern", "")
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return pd.Series(False, index=df.index), f"Invalid regex pattern: {e}"
    s = df[col].dropna().astype(str)
    mask = s.map(lambda v: bool(rx.search(v)))
    full_mask = pd.Series(True, index=df.index)
    full_mask.loc[s.index] = mask
    return full_mask, None


@register_rule("email_format")
def check_email(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    s = df[col].dropna().astype(str)
    mask = s.map(lambda v: bool(EMAIL_REGEX.match(v)))
    full_mask = pd.Series(True, index=df.index)
    full_mask.loc[s.index] = mask
    return full_mask, None


# ---------------- Categorical Rules ----------------
@register_rule("in_set")
def check_in_set(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    allowed = set(params.get("allowed_values", []))
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    s = df[col].dropna()
    # Normalize comparison to strings
    allowed_str = {str(x).strip().lower() for x in allowed}
    mask = s.map(lambda v: str(v).strip().lower() in allowed_str)
    full_mask = pd.Series(True, index=df.index)
    full_mask.loc[s.index] = mask
    return full_mask, None


@register_rule("not_in_set")
def check_not_in_set(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    prohibited = set(params.get("prohibited_values", []))
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    s = df[col].dropna()
    prohibited_str = {str(x).strip().lower() for x in prohibited}
    mask = s.map(lambda v: str(v).strip().lower() not in prohibited_str)
    full_mask = pd.Series(True, index=df.index)
    full_mask.loc[s.index] = mask
    return full_mask, None


# ---------------- Date Rules ----------------
@register_rule("not_future_date")
def check_not_future_date(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    now = pd.Timestamp.now(tz=timezone.utc)
    dates = pd.to_datetime(df[col], errors="coerce", format="mixed", utc=True)
    return dates <= now, None


@register_rule("start_before_end_date")
def check_date_order(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    if len(target_columns) < 2:
        return pd.Series(False, index=df.index), "start_before_end_date requires 2 columns [start_col, end_col]"
    start_col, end_col = target_columns[0], target_columns[1]
    if start_col not in df.columns or end_col not in df.columns:
        return pd.Series(False, index=df.index), f"Columns '{start_col}' or '{end_col}' missing"
    d_start = pd.to_datetime(df[start_col], errors="coerce", format="mixed")
    d_end = pd.to_datetime(df[end_col], errors="coerce", format="mixed")
    return d_start <= d_end, None


# ---------------- Cross-Column ----------------
@register_rule("col_a_lte_col_b")
def check_col_a_lte_col_b(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    if len(target_columns) < 2:
        return pd.Series(False, index=df.index), "col_a_lte_col_b requires 2 columns [col_a, col_b]"
    col_a, col_b = target_columns[0], target_columns[1]
    if col_a not in df.columns or col_b not in df.columns:
        return pd.Series(False, index=df.index), f"Columns '{col_a}' or '{col_b}' missing"
    num_a = pd.to_numeric(df[col_a], errors="coerce")
    num_b = pd.to_numeric(df[col_b], errors="coerce")
    return num_a <= num_b, None


# ---------------- Statistical Rules ----------------
@register_rule("iqr_outlier_check")
def check_iqr_outliers(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    factor = float(params.get("factor", 1.5))
    num_s = pd.to_numeric(df[col], errors="coerce").dropna()
    if num_s.empty:
        return pd.Series(True, index=df.index), None
    q1 = num_s.quantile(0.25)
    q3 = num_s.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    is_valid = (df[col].isna()) | ((pd.to_numeric(df[col], errors="coerce") >= lower_bound) & (pd.to_numeric(df[col], errors="coerce") <= upper_bound))
    return is_valid, None


@register_rule("zscore_outlier_check")
def check_zscore_outliers(df: pd.DataFrame, target_columns: List[str], params: Dict[str, Any]) -> Tuple[pd.Series, Optional[str]]:
    col = target_columns[0]
    if col not in df.columns:
        return pd.Series(False, index=df.index), f"Column '{col}' not in dataset"
    threshold = float(params.get("threshold", 3.0))
    num_s = pd.to_numeric(df[col], errors="coerce")
    valid_vals = num_s.dropna()
    if len(valid_vals) <= 1 or valid_vals.std() == 0:
        return pd.Series(True, index=df.index), None
    mean = valid_vals.mean()
    std = valid_vals.std()
    z_scores = (num_s - mean).abs() / std
    is_valid = num_s.isna() | (z_scores <= threshold)
    return is_valid, None
