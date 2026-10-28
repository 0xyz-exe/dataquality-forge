import sys
from pathlib import Path
import httpx

API_URL = "http://127.0.0.1:8000"


def seed():
    with httpx.Client(base_url=API_URL, timeout=30.0) as client:
        # Check health
        res = client.get("/health/live")
        if res.status_code != 200:
            print("API not responding")
            sys.exit(1)

        # Create Project 1
        p1 = client.post("/api/v1/projects", json={
            "name": "E-Commerce Customer Master",
            "description": "Production customer registry and transactional logs verification."
        }).json()
        print(f"Created project: {p1['name']}")

        # Upload customers.csv
        with open("examples/customers.csv", "rb") as f:
            d1 = client.post(
                "/api/v1/datasets",
                data={"project_id": p1["id"], "name": "Customers Q3 Master", "description": "Customer demographic and identity profile"},
                files={"file": ("customers.csv", f, "text/csv")},
            ).json()
        print(f"Uploaded dataset: {d1['name']}")

        # Profile d1
        client.post(f"/api/v1/datasets/{d1['id']}/profile")
        print("Profile generated for d1")

        # Rules for d1
        rules = [
            {"name": "ID Not Null", "rule_type": "not_null", "target_columns": ["id"], "severity": "CRITICAL"},
            {"name": "ID Must Be Unique", "rule_type": "unique_column", "target_columns": ["id"], "severity": "CRITICAL"},
            {"name": "Email RFC Syntax", "rule_type": "email_format", "target_columns": ["email"], "severity": "ERROR"},
            {"name": "Age 0-120 Range", "rule_type": "value_between", "target_columns": ["age"], "parameters": {"min_value": 0, "max_value": 120}, "severity": "ERROR"},
            {"name": "Country Code ISO", "rule_type": "in_set", "target_columns": ["country"], "parameters": {"allowed_values": ["USA", "CAN", "GBR", "FRA", "DEU"]}, "severity": "WARNING"},
            {"name": "Signup Date Not Future", "rule_type": "not_future_date", "target_columns": ["signup_date"], "severity": "ERROR"},
        ]
        for r in rules:
            client.post(f"/api/v1/datasets/{d1['id']}/rules", json=r)

        # Run validation on d1
        v1 = client.post(f"/api/v1/datasets/{d1['id']}/validation-runs").json()
        print(f"Validation executed. Quality Score: {v1['quality_score']}%")

        # Create Project 2
        p2 = client.post("/api/v1/projects", json={
            "name": "Fulfillment & Orders Pipeline",
            "description": "Supply chain logistics, order items, and payment gateway logs."
        }).json()

        # Upload orders.csv
        with open("examples/orders.csv", "rb") as f:
            d2 = client.post(
                "/api/v1/datasets",
                data={"project_id": p2["id"], "name": "Order Fulfillment Stream", "description": "Delivery dispatch log"},
                files={"file": ("orders.csv", f, "text/csv")},
            ).json()

        client.post(f"/api/v1/datasets/{d2['id']}/profile")

        client.post(f"/api/v1/datasets/{d2['id']}/rules", json={
            "name": "Order Date Before Delivery Date",
            "rule_type": "start_before_end_date",
            "target_columns": ["order_date", "delivery_date"],
            "severity": "ERROR"
        })
        client.post(f"/api/v1/datasets/{d2['id']}/rules", json={
            "name": "Total Amount Positive",
            "rule_type": "min_value",
            "target_columns": ["total_amount"],
            "parameters": {"min_value": 0},
            "severity": "CRITICAL"
        })
        v2 = client.post(f"/api/v1/datasets/{d2['id']}/validation-runs").json()
        print(f"Second validation executed. Quality Score: {v2['quality_score']}%")

        print("Seeding completed successfully!")


if __name__ == "__main__":
    seed()
