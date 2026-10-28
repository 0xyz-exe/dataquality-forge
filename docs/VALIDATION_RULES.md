# Validation Rules Reference

DataQuality Forge implements 10 declarative validation families.

| Family | Rule Type | Description | Target Parameters |
|---|---|---|---|
| **Completeness** | `not_null` | Column must not contain null/NaN values | `target_columns` |
| | `max_null_percentage` | Null values cannot exceed threshold | `max_percentage` |
| | `not_empty_string` | String values cannot be empty `""` | `target_columns` |
| | `not_whitespace` | Values cannot contain only whitespaces | `target_columns` |
| **Uniqueness** | `unique_column` | Column values must be distinct | `target_columns` |
| | `unique_composite` | Combination of columns must be unique | `target_columns` (multi) |
| | `no_duplicate_rows` | Entire row must not be duplicated | - |
| **Type** | `is_type` | Values must conform to target type | `expected_type` |
| **Range** | `min_value` | Numeric value must be >= minimum | `min_value` |
| | `max_value` | Numeric value must be <= maximum | `max_value` |
| | `value_between` | Numeric value within range | `min_value`, `max_value` |
| | `string_length_between` | String length within bounds | `min_length`, `max_length` |
| **Pattern** | `regex_match` | Conforms to regular expression | `pattern` |
| | `email_format` | Valid RFC email syntax | `target_columns` |
| **Categorical** | `in_set` | Must exist in allowed set | `allowed_values` |
| | `not_in_set` | Must not exist in prohibited set | `prohibited_values` |
| **Date** | `not_future_date` | Timestamp cannot exceed UTC now | `target_columns` |
| | `start_before_end_date` | Date A <= Date B | `[col_a, col_b]` |
| **Cross-Column** | `col_a_lte_col_b` | Numeric Column A <= Column B | `[col_a, col_b]` |
| **Statistical** | `iqr_outlier_check` | Within Q1 - 1.5*IQR and Q3 + 1.5*IQR | `factor` (default 1.5) |
| | `zscore_outlier_check` | Abs(Z-Score) <= threshold | `threshold` (default 3.0) |
