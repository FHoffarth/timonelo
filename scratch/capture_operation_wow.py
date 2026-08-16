from playwright.sync_api import sync_playwright
import os

ARTIFACT_DIR = "C:/Users/Flo/.gemini/antigravity/brain/20d31e34-a159-4223-a758-2695e9de02c4"

def capture_operation_wow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. Cabin Experience with the new Signature Interactive Silhouette
        print("Capturing 10_cabin_signature_silhouette.png...")
        page.goto("http://localhost:5173/msc-bellissima/cabin/14122")
        page.wait_for_selector("text=Architectural Cross-Section")
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "10_cabin_signature_silhouette.png"), full_page=False)

        # 2. Dedicated Ship Landing Page
        print("Capturing 11_ship_landing_bellissima.png...")
        page.goto("http://localhost:5173/vessels/msc-bellissima")
        page.wait_for_selector("text=MSC Bellissima")
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "11_ship_landing_bellissima.png"), full_page=False)

        # 3. Port Explorer - Genoa
        print("Capturing 12_port_explorer_genoa.png...")
        page.goto("http://localhost:5173/ports")
        page.wait_for_selector("text=Port of Genoa")
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "12_port_explorer_genoa.png"), full_page=False)

        # 4. Crew Onboard Invitation
        print("Capturing 13_crew_invitation.png...")
        page.goto("http://localhost:5173/crew")
        page.wait_for_selector("text=An Invitation to the Crew")
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "13_crew_invitation.png"), full_page=False)

        # 5. Universal Search
        print("Capturing 14_universal_search.png...")
        page.goto("http://localhost:5173/")
        page.click("button:has-text('Search')")
        page.wait_for_selector("input[placeholder*='Search vessels']")
        page.fill("input[placeholder*='Search vessels']", "14122")
        page.wait_for_selector("text=Cabin 14122 (MSC Bellissima)")
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "14_universal_search.png"), full_page=False)

        browser.close()
        print("All Operation WOW screenshots captured successfully.")

if __name__ == "__main__":
    capture_operation_wow()
