from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Load the local HTML file
        page.goto(f"file://{os.path.abspath('liveworksheet_clone.html')}")
        # Take a screenshot
        page.screenshot(path="/home/jules/verification/clone_layout_v10.png")
        browser.close()

if __name__ == "__main__":
    run()
