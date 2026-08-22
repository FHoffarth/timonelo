import argparse
import os
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "knowledge" / "reports" / "screenshots"

def run(artifacts_dir: Path = DEFAULT_OUTPUT_DIR):
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        
        print("1. Opening app...")
        page.goto("http://localhost:5173", wait_until="networkidle")
        page.wait_for_timeout(1000)
        
        # Click Knowledge Factory in navbar
        print("2. Navigating to Knowledge Factory...")
        page.get_by_role("button", name="Knowledge Factory").click()
        page.wait_for_timeout(1500)
        
        print("Saving 01_knowledge_dashboard_hero.png...")
        page.screenshot(path=str(artifacts_dir / "01_knowledge_dashboard_hero.png"))
        
        # Scroll to Artifact Queue & Conflict Log
        page.evaluate("window.scrollTo({ top: 480, behavior: 'instant' });")
        page.wait_for_timeout(1000)
        print("Saving 02_knowledge_artifact_queue_conflicts.png...")
        page.screenshot(path=str(artifacts_dir / "02_knowledge_artifact_queue_conflicts.png"))
        
        # Scroll to Fleet Readiness Matrix
        page.evaluate("window.scrollTo({ top: 900, behavior: 'instant' });")
        page.wait_for_timeout(1000)
        print("Saving 03_knowledge_fleet_readiness_matrix.png...")
        page.screenshot(path=str(artifacts_dir / "03_knowledge_fleet_readiness_matrix.png"))

        browser.close()
        print("Captured all knowledge dashboard screenshots successfully!")

def main():
    parser = argparse.ArgumentParser(description="Capture knowledge dashboard screenshots.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Output screenshot directory (default: {DEFAULT_OUTPUT_DIR})")
    args = parser.parse_args()

    run(args.output_dir)

if __name__ == "__main__":
    main()
