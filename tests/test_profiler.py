import pytest
from dataquality_forge.profiler import profile_dataset


def test_profiler_customers(tmp_path):
    csv_file = "examples/customers.csv"
    res = profile_dataset(csv_file)
    assert res["total_rows"] == 11
    assert res["total_columns"] == 7
    assert res["duplicate_rows"] == 1
    assert res["missing_cells"] == 1  # 1 missing email
    assert len(res["column_profiles"]) == 7

    col_map = {c["name"]: c for c in res["column_profiles"]}
    assert "email" in col_map
    assert col_map["email"]["null_count"] == 1
    assert "age" in col_map
    assert col_map["age"]["numeric_stats"] is not None


def test_profiler_empty_dataset(tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("a,b,c\n", encoding="utf-8")
    res = profile_dataset(str(empty_csv))
    assert res["total_rows"] == 0
    assert res["total_columns"] == 3
