import os
import time
from playwright.sync_api import sync_playwright

def run():
    artifacts_dir = r"C:\Users\Flo\.gemini\antigravity\brain\20d31e34-a159-4223-a758-2695e9de02c4"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("1. Opening app...")
        page.goto("http://localhost:5173", wait_until="networkidle")
        page.wait_for_timeout(1000)
        
        # Click on Ships in navbar
        print("2. Clicking navbar Ships...")
        page.get_by_role("button", name="Ships").click()
        page.wait_for_timeout(1000)
        
        # Click on Living Deck tab
        print("3. Clicking Living Deck tab...")
        page.get_by_role("button", name="Living Deck", exact=True).click()
        page.wait_for_timeout(1000)
        
        # Scroll the living deck container directly into full view
        print("4. Scrolling Living Deck into center view...")
        deck_container = page.locator("text=DeckNavigationTree").locator("..").first
        page.evaluate("window.scrollTo({ top: 580, behavior: 'instant' });")
        page.wait_for_timeout(1000)
        
        print("5. Saving 01_living_deck_full_canvas.png...")
        page.screenshot(path=os.path.join(artifacts_dir, "01_living_deck_full_canvas.png"))
        
        # Click on a cabin in the CabinLayer
        print("6. Clicking cabin stateroom...")
        cabin = page.locator("#cabin-layer rect").first
        if cabin.is_visible():
            cabin.click()
            page.wait_for_timeout(1000)
            print("Saving 02_cabin_selection_active.png...")
            page.screenshot(path=os.path.join(artifacts_dir, "02_cabin_selection_active.png"))
            
        # Switch to Deck 6 to showcase venues and restaurants
        print("7. Clicking Deck 6 in DeckNavigationTree...")
        deck_6 = page.locator("text=Deck 6").first
        if deck_6.is_visible():
            deck_6.click()
            page.wait_for_timeout(1500)
            print("Saving 03_deck6_venues_layer.png...")
            page.screenshot(path=os.path.join(artifacts_dir, "03_deck6_venues_layer.png"))
            
        # Hover on LiftLayer
        print("8. Hovering over lift core...")
        lift = page.locator("#lift-layer rect").first
        if lift.is_visible():
            lift.hover()
            page.wait_for_timeout(1000)
            print("Saving 04_lift_layer_active.png...")
            page.screenshot(path=os.path.join(artifacts_dir, "04_lift_layer_active.png"))
            
        # Test Zoom In
        print("9. Clicking Zoom In...")
        zoom_btn = page.locator("button[title='Zoom In']")
        if zoom_btn.is_visible():
            zoom_btn.click()
            zoom_btn.click()
            page.wait_for_timeout(1000)
            print("Saving 05_zoomed_canvas.png...")
            page.screenshot(path=os.path.join(artifacts_dir, "05_zoomed_canvas.png"))

        browser.close()
        print("Done!")

if __name__ == "__main__":
    run()
