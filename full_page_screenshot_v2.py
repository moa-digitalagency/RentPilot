
"""
* Nom de l'application : RentPilot
* Description : Source file: full_page_screenshot_v2.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5000")
        page.screenshot(path="verification/landing_v2_full.png", full_page=True)
        browser.close()

if __name__ == "__main__":
    run()