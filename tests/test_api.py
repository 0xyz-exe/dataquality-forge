import pytest
from fastapi.testclient import TestClient
from dataquality_forge.api.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health/live")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_project_crud_and_dataset():
    # Create project
    proj_res = client.post("/api/v1/projects", json={"name": "Test Project", "description": "Test"})
    assert proj_res.status_code == 200
    proj_id = proj_res.json()["id"]

    # Upload dataset
    with open("examples/customers.csv", "rb") as f:
        upload_res = client.post(
            "/api/v1/datasets",
            data={"project_id": proj_id, "name": "Customers Sample"},
            files={"file": ("customers.csv", f, "text/csv")},
        )
    assert upload_res.status_code == 200
    ds_id = upload_res.json()["id"]

    # Preview dataset
    preview_res = client.get(f"/api/v1/datasets/{ds_id}/preview")
    assert preview_res.status_code == 200
    assert len(preview_res.json()["rows"]) > 0

    # Profile dataset
    prof_res = client.post(f"/api/v1/datasets/{ds_id}/profile")
    assert prof_res.status_code == 200
    assert prof_res.json()["summary"]["total_rows"] == 11

    # Create validation rule
    rule_res = client.post(
        f"/api/v1/datasets/{ds_id}/rules",
        json={"name": "Age > 0", "rule_type": "min_value", "target_columns": ["age"], "parameters": {"min_value": 0}},
    )
    assert rule_res.status_code == 200

    # Run validation
    val_res = client.post(f"/api/v1/datasets/{ds_id}/validation-runs")
    assert val_res.status_code == 200
    run_id = val_res.json()["run_id"]

    # Export report
    rep_res = client.get(f"/api/v1/validation-runs/{run_id}/report?format=html")
    assert rep_res.status_code == 200
    assert "DataQuality Forge Validation Report" in rep_res.text
