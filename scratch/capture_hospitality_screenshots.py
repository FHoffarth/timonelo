import os
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\Flo\.gemini\antigravity\brain\20d31e34-a159-4223-a758-2695e9de02c4"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

viewports = [
    {"name": "01_desktop_1440_hero", "width": 1440, "height": 900, "full_page": False},
    {"name": "02_desktop_1440_full", "width": 1440, "height": 900, "full_page": True},
    {"name": "03_laptop_1280_hero", "width": 1280, "height": 800, "full_page": False},
    {"name": "04_laptop_1280_full", "width": 1280, "height": 800, "full_page": True},
    {"name": "05_tablet_768_hero", "width": 768, "height": 1024, "full_page": False},
    {"name": "06_tablet_768_full", "width": 768, "height": 1024, "full_page": True},
    {"name": "07_iphone15_390_hero", "width": 390, "height": 844, "full_page": False},
    {"name": "08_iphone15_390_full", "width": 390, "height": 844, "full_page": True},
    {"name": "09_mobile_320_hero", "width": 320, "height": 568, "full_page": False},
    {"name": "10_mobile_320_full", "width": 320, "height": 568, "full_page": True},
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    for vp in viewports:
        context = browser.new_context(
            viewport={"width": vp["width"], "height": vp["height"]},
            device_scale_factor=2,  # Retina high-DPI quality
        )
        page = context.new_page()
        page.goto("http://localhost:5173", wait_until="networkidle")
        time.sleep(1.0)  # Wait for fonts & layout stabilization
        
        output_path = os.path.join(ARTIFACT_DIR, f"{vp['name']}.png")
        page.screenshot(path=output_path, full_page=vp["full_page"])
        print(f"Captured: {output_path} (full_page={vp['full_page']})")
        context.close()
        
    browser.close()

print("All screenshots successfully captured in high-DPI.")
