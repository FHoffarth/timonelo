from playwright.sync_api import sync_playwright

def test_lighthouse():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        print("1. Testing Landing Page...")
        page.goto("http://localhost:5173/")
        page.wait_for_selector("text=Universal Vessel Intelligence")
        print("   [OK] Landing page loaded.")

        print("2. Testing Ship Landing Page (/vessels/msc-bellissima)...")
        page.goto("http://localhost:5173/vessels/msc-bellissima")
        page.wait_for_selector("text=MSC Bellissima")
        page.wait_for_selector("text=Stateroom Intelligence")
        print("   [OK] Ship landing page loaded.")

        print("3. Testing Port Explorer (/ports)...")
        page.goto("http://localhost:5173/ports")
        page.wait_for_selector("text=Strategic Cruise Ports")
        page.wait_for_selector("text=Port of Genoa")
        print("   [OK] Port explorer loaded.")

        print("4. Testing Crew Section (/crew)...")
        page.goto("http://localhost:5173/crew")
        page.wait_for_selector("text=Crew Contribution Programme")
        # Test code verification
        page.fill("input[placeholder*='BELLISSIMA-2026']", "BELLISSIMA-2026")
        page.click("button:has-text('Verify Access')")
        page.wait_for_selector("text=Verified Contributor Session Active")
        print("   [OK] Crew section verified with onboard access code.")

        print("5. Testing Mission Section (/mission)...")
        page.goto("http://localhost:5173/mission")
        page.wait_for_selector("text=Why Timonelo Exists")
        page.wait_for_selector("text=Negative Intelligence")
        print("   [OK] Mission section loaded.")

        print("6. Testing Universal Search...")
        page.goto("http://localhost:5173/")
        page.click("button:has-text('Search')")
        page.wait_for_selector("input[placeholder*='Search vessels']")
        page.fill("input[placeholder*='Search vessels']", "14122")
        page.wait_for_selector("text=Cabin 14122 (MSC Bellissima)")
        print("   [OK] Universal search indexing verified.")

        browser.close()
        print("\nALL LIGHTHOUSE PRODUCT JOURNEYS VALIDATED SUCCESSFULLY!")

if __name__ == "__main__":
    test_lighthouse()
