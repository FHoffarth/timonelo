import os
import time
from playwright.sync_api import sync_playwright

def run():
    artifacts_dir = r"C:\Users\Flo\.gemini\antigravity\brain\20d31e34-a159-4223-a758-2695e9de02c4"
    
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
        page.screenshot(path=os.path.join(artifacts_dir, "01_knowledge_dashboard_hero.png"))
        
        # Scroll to Artifact Queue & Conflict Log
        page.evaluate("window.scrollTo({ top: 480, behavior: 'instant' });")
        page.wait_for_timeout(1000)
        print("Saving 02_knowledge_artifact_queue_conflicts.png...")
        page.screenshot(path=os.path.join(artifacts_dir, "02_knowledge_artifact_queue_conflicts.png"))
        
        # Scroll to Fleet Readiness Matrix
        page.evaluate("window.scrollTo({ top: 900, behavior: 'instant' });")
        page.wait_for_timeout(1000)
        print("Saving 03_knowledge_fleet_readiness_matrix.png...")
        page.screenshot(path=os.path.join(artifacts_dir, "03_knowledge_fleet_readiness_matrix.png"))

        browser.close()
        print("Captured all knowledge dashboard screenshots successfully!")

if __name__ == "__main__":
    run()
