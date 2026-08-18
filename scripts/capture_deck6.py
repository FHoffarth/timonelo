import os
import time
from playwright.sync_api import sync_playwright

def run():
    artifacts_dir = r"C:\Users\Flo\.gemini\antigravity\brain\20d31e34-a159-4223-a758-2695e9de02c4"
    
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
        page.screenshot(path=os.path.join(artifacts_dir, "03_deck6_venues_layer.png"))

        browser.close()
        print("Captured Deck 6!")

if __name__ == "__main__":
    run()
