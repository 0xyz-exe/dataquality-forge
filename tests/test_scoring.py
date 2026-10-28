import pytest
from dataquality_forge.scoring import calculate_quality_score


def test_scoring_empty():
    assert calculate_quality_score([]) is None


def test_scoring_weights():
    # 1 critical rule (weight 4) with 10 passed out of 10
    # 1 warning rule (weight 1.5) with 0 passed out of 10
    results = [
        {"rule_name": "R1", "severity": "CRITICAL", "total_records": 10, "passed_records": 10, "failed_records": 0, "pass_percentage": 100.0},
        {"rule_name": "R2", "severity": "WARNING", "total_records": 10, "passed_records": 0, "failed_records": 10, "pass_percentage": 0.0},
    ]
    # Total weighted: (10 * 4) + (0 * 1.5) = 40. Total possible: (10 * 4) + (10 * 1.5) = 55.
    # Score: 40 / 55 * 100 = 72.73%
    score_res = calculate_quality_score(results)
    assert score_res is not None
    assert score_res["score"] == 72.73
    assert score_res["total_checks"] == 20
    assert score_res["failed_checks"] == 10
