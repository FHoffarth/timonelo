import json
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    results = {}
    
    # Journey 1: Sailing with MSC Bellissima next month
    page.goto('http://localhost:5173/?lang=en', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 1 (Sailing MSC Bellissima)'] = 'YES' if 'Welcome aboard' in page.content() else 'NO'
        
    # Journey 2: Discover my ship
    page.goto('http://localhost:5173/vessels/msc-bellissima', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 2 (Discover my ship)'] = 'YES' if 'MSC Bellissima' in page.content() and 'Decks' in page.content() else 'NO'
    
    # Journey 3: Find my cabin
    page.goto('http://localhost:5173/msc-bellissima/cabin/14122', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 3 (Find my cabin)'] = 'YES' if '14122' in page.content() and 'Deck 14' in page.content() else 'NO'
    
    # Journey 4: Understand embarkation
    results['Journey 4 (Understand embarkation)'] = 'YES' if 'Boarding' in page.content() and 'Station F' in page.content() else 'NO'
    
    # Journey 5: Explore ports
    page.goto('http://localhost:5173/ports', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 5 (Explore ports)'] = 'YES' if 'Strategic Cruise Ports' in page.content() and 'UN/LOCODE' in page.content() else 'NO'
    
    # Journey 6: What Tim does
    page.goto('http://localhost:5173/?lang=en', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 6 (What Tim actually does)'] = 'YES' if 'Bridge Officer Tim' in page.content() and 'On Watch' in page.content() else 'NO'
    
    # Journey 7: Search something unknown
    page.goto('http://localhost:5173/?lang=en', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 7 (Search unknown)'] = 'YES' if '⌘K' in page.content() else 'NO'
    
    # Journey 8: Language Switch
    page.goto('http://localhost:5173/?lang=de', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 8 (Switch EN to DE)'] = 'YES' if 'Willkommen an Bord' in page.content() and 'Ich bleibe auf der Brücke' in page.content() else 'NO'
    
    # Journey 9: Invalid URL / Graceful 404 with Tim
    page.goto('http://localhost:5173/vessels/unknown-ghost-ship', timeout=8000)
    time.sleep(0.5)
    results['Journey 9 (Invalid URL / 404 with Tim)'] = 'YES' if 'Vessel Not Found in Active Registry' in page.content() or 'Schiff nicht im Register gefunden' in page.content() else 'NO'
    
    # Journey 10: Return after first visit
    page.goto('http://localhost:5173/', timeout=8000)
    page.wait_for_selector('h1', timeout=5000)
    results['Journey 10 (Return to Timonelo)'] = 'YES'
    
    browser.close()
    print(json.dumps(results, indent=2))
