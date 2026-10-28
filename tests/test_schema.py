import pytest
from dataquality_forge.schema import extract_schema_from_file, compare_schemas


def test_schema_comparison():
    expected = {
        "id": {"type": "integer", "nullable": False},
        "name": {"type": "string", "nullable": False},
        "email": {"type": "string", "nullable": False},
        "missing_col": {"type": "string", "nullable": True},
    }
    actual = {
        "id": {"type": "integer", "nullable": False},
        "name": {"type": "string", "nullable": False},
        "email": {"type": "string", "nullable": True},  # violated nullability
        "added_col": {"type": "float", "nullable": True},
    }

    diff = compare_schemas(expected, actual)
    assert not diff["is_compatible"]
    assert "missing_col" in diff["missing_columns"]
    assert "added_col" in diff["added_columns"]
    assert len(diff["nullability_changes"]) == 1
    assert len(diff["breaking_changes"]) == 2  # missing_col and email nullability
