from typing import List, Dict, Any, Optional

SEVERITY_WEIGHTS = {
    "CRITICAL": 4.0,
    "ERROR": 3.0,
    "WARNING": 1.5,
    "INFO": 0.5,
}


def calculate_quality_score(rule_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not rule_results:
        return None

    weighted_passed = 0.0
    weighted_total = 0.0
    rules_breakdown = []
    total_checks = 0
    failed_checks = 0

    for r in rule_results:
        sev = r.get("severity", "ERROR").upper()
        weight = SEVERITY_WEIGHTS.get(sev, 2.0)
        tot = r.get("total_records", 0)
        pas = r.get("passed_records", 0)
        fai = r.get("failed_records", 0)

        weighted_passed += pas * weight
        weighted_total += tot * weight
        total_checks += tot
        failed_checks += fai

        rules_breakdown.append({
            "rule_name": r.get("rule_name"),
            "severity": sev,
            "weight": weight,
            "passed_records": pas,
            "total_records": tot,
            "rule_pass_percentage": r.get("pass_percentage", 100.0)
        })

    if weighted_total == 0:
        return {
            "score": 100.0,
            "weighted_passed": 0.0,
            "weighted_total": 0.0,
            "formula": "weighted_passed / weighted_total * 100",
            "weights": SEVERITY_WEIGHTS,
            "total_checks": total_checks,
            "failed_checks": failed_checks,
            "breakdown": rules_breakdown,
            "summary": "No evaluation records processed; default score 100.0%."
        }

    score = round((weighted_passed / weighted_total) * 100, 2)

    return {
        "score": score,
        "weighted_passed": round(weighted_passed, 2),
        "weighted_total": round(weighted_total, 2),
        "formula": "weighted_passed_checks / weighted_evaluated_checks * 100",
        "weights": SEVERITY_WEIGHTS,
        "total_checks": total_checks,
        "failed_checks": failed_checks,
        "breakdown": rules_breakdown,
        "summary": f"Calculated quality score of {score}% across {len(rule_results)} rules and {total_checks} records."
    }
