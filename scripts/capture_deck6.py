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
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        page.goto("http://localhost:5173", wait_until="networkidle")
        page.wait_for_timeout(1000)
        
        # Click Ships in navbar
        page.get_by_role("button", name="Ships").click()
        page.wait_for_timeout(1000)
        
        # Click Living Deck
        page.get_by_role("button", name="Living Deck", exact=True).click()
        page.wait_for_timeout(1000)
        
        page.evaluate("window.scrollTo({ top: 580, behavior: 'instant' });")
        page.wait_for_timeout(500)
        
        # Click Deck 6 button in deck navigation tree
        deck_buttons = page.locator("button:has-text('6')")
        for i in range(deck_buttons.count()):
            btn = deck_buttons.nth(i)
            if "6" in btn.inner_text() and ("Level" in btn.inner_text() or "Spaces" in btn.inner_text() or "Musica" in btn.inner_text() or "6" == btn.inner_text().strip()):
                btn.click()
                break
                
        page.wait_for_timeout(1500)
        print("Saving 03_deck6_venues_layer.png...")
        page.screenshot(path=str(artifacts_dir / "03_deck6_venues_layer.png"))

        browser.close()
        print("Captured Deck 6!")

def main():
    parser = argparse.ArgumentParser(description="Capture Deck 6 screenshot.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Output screenshot directory (default: {DEFAULT_OUTPUT_DIR})")
    args = parser.parse_args()

    run(args.output_dir)

if __name__ == "__main__":
    main()
