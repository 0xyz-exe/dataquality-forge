import time
from pathlib import Path
import httpx
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def capture():
    res = httpx.get("http://127.0.0.1:8000/api/v1/datasets")
    datasets = res.json()
    first_ds_id = datasets[0]["id"] if datasets else None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Overview
        page.goto("http://127.0.0.1:3000/")
        page.wait_for_selector("text=Platform Overview", timeout=10000)
        time.sleep(2)
        page.screenshot(path=str(OUT_DIR / "overview.png"), full_page=False)
        print("Captured overview.png")

        # 2. Dataset Detail
        if first_ds_id:
            page.goto(f"http://127.0.0.1:3000/datasets/{first_ds_id}")
            time.sleep(2)
            page.screenshot(path=str(OUT_DIR / "dataset_detail.png"), full_page=False)
            print("Captured dataset_detail.png")

            # Click Column Profiles tab
            page.locator("button:has-text('Column Profiles')").click()
            time.sleep(2)
            page.screenshot(path=str(OUT_DIR / "dataset_profiling.png"), full_page=False)
            print("Captured dataset_profiling.png")

            # Click Runs tab
            page.locator("button:has-text('Runs')").click()
            time.sleep(2)
            page.screenshot(path=str(OUT_DIR / "validation_runs.png"), full_page=False)
            print("Captured validation_runs.png")

        # 3. Schema Registry
        page.goto("http://127.0.0.1:3000/schema")
        page.wait_for_selector("text=Schema Registry & Evolution", timeout=10000)
        time.sleep(2)
        page.screenshot(path=str(OUT_DIR / "schema_registry.png"), full_page=False)
        print("Captured schema_registry.png")

        browser.close()


if __name__ == "__main__":
    capture()
