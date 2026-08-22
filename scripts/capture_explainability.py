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
        
        # Click Ships in navbar
        print("2. Navigating to MSC Bellissima...")
        page.get_by_role("button", name="Ships").click()
        page.wait_for_timeout(1000)
        
        # Click Cabins Tab
        print("3. Clicking Cabins tab...")
        page.get_by_role("button", name="Cabins", exact=True).click()
        page.wait_for_timeout(1000)
        
        # Click Inspect Cabin 14122
        print("4. Opening Cabin 14122 Deep Dive Page...")
        page.get_by_role("button", name="Inspect Cabin 14122 →").click()
        page.wait_for_timeout(1500)
        
        # Scroll to Explainability Card
        page.evaluate("window.scrollTo({ top: 1200, behavior: 'instant' });")
        page.wait_for_timeout(1000)
        
        print("Saving 01_explainability_card_walkthrough.png...")
        page.screenshot(path=str(artifacts_dir / "01_explainability_card_walkthrough.png"))
        
        # Click Evidence Classification tab
        print("Clicking Evidence tab...")
        page.get_by_role("button", name="Evidence Classification").click()
        page.wait_for_timeout(800)
        
        print("Saving 02_explainability_evidence_classification.png...")
        page.screenshot(path=str(artifacts_dir / "02_explainability_evidence_classification.png"))
        
        # Click Living Deck tab in ship profile
        print("5. Opening Living Deck with 'Why?' in Inspector...")
        page.get_by_role("button", name="MSC Bellissima").first.click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Living Deck", exact=True).click()
        page.wait_for_timeout(1000)
        
        # Click Why? button in inspector
        page.get_by_role("button", name="Why? (Evidence Trace) ▼").click()
        page.wait_for_timeout(800)
        
        page.evaluate("window.scrollTo({ top: 580, behavior: 'instant' });")
        page.wait_for_timeout(1000)
        
        print("Saving 03_living_deck_why_trace_inspector.png...")
        page.screenshot(path=str(artifacts_dir / "03_living_deck_why_trace_inspector.png"))

        browser.close()
        print("Captured all explainability screenshots successfully!")

def main():
    parser = argparse.ArgumentParser(description="Capture explainability screenshots.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Output screenshot directory (default: {DEFAULT_OUTPUT_DIR})")
    args = parser.parse_args()

    run(args.output_dir)

if __name__ == "__main__":
    main()
