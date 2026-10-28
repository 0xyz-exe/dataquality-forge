import pytest
import pandas as pd
from dataquality_forge.validator import execute_validation_run


def test_validation_customers():
    csv_file = "examples/customers.csv"
    rules = [
        {"name": "ID Not Null", "rule_type": "not_null", "target_columns": ["id"], "severity": "CRITICAL"},
        {"name": "ID Unique", "rule_type": "unique_column", "target_columns": ["id"], "severity": "CRITICAL"},
        {"name": "Valid Email", "rule_type": "email_format", "target_columns": ["email"], "severity": "ERROR"},
        {"name": "Age Positive", "rule_type": "min_value", "target_columns": ["age"], "parameters": {"min_value": 0}, "severity": "ERROR"},
        {"name": "Country Valid", "rule_type": "in_set", "target_columns": ["country"], "parameters": {"allowed_values": ["USA", "CAN", "GBR", "FRA", "DEU"]}, "severity": "WARNING"},
    ]

    res = execute_validation_run(csv_file, rules)
    assert res["status"] == "completed"
    assert res["rules_executed"] == 5
    assert res["failed_rules"] >= 3  # ID unique fails (duplicate 1), Valid Email fails, Age fails (-5), Country fails
    assert res["quality_score"] is not None
    assert 0 <= res["quality_score"] <= 100


def test_cross_column_rules(tmp_path):
    f = tmp_path / "dates.csv"
    f.write_text("start_date,end_date,min_qty,max_qty\n2023-01-01,2023-01-05,10,20\n2023-02-10,2023-02-01,50,40\n", encoding="utf-8")
    rules = [
        {"name": "Start Before End", "rule_type": "start_before_end_date", "target_columns": ["start_date", "end_date"], "severity": "ERROR"},
        {"name": "Min Qty LTE Max Qty", "rule_type": "col_a_lte_col_b", "target_columns": ["min_qty", "max_qty"], "severity": "ERROR"},
    ]
    res = execute_validation_run(str(f), rules)
    assert res["rules_executed"] == 2
    # Second row in both rules violates condition
    assert res["rule_results"][0]["passed_records"] == 1
    assert res["rule_results"][0]["failed_records"] == 1
    assert res["rule_results"][1]["passed_records"] == 1
    assert res["rule_results"][1]["failed_records"] == 1
