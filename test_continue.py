import sys, time
sys.path.append('c:/resrise-studio')
from scripts.core.config import get_settings
from playwright.sync_api import sync_playwright

settings = get_settings()
user_data_dir = settings.get_chrome_profile_dir('mairamehraofficial')

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        channel='chrome',
        args=['--disable-blink-features=AutomationControlled']
    )
    page = browser.new_page()
    page.goto('https://www.instagram.com/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(2.0)
    
    # Check for Continue button
    continue_btn = page.locator("button:has-text('Continue')").first
    if continue_btn.is_visible(timeout=3000):
        print('Found Continue button! Clicking it...')
        continue_btn.click(force=True)
        time.sleep(5.0)
        
    print('After click URL:', page.url)
    print('After click Title:', page.title())
    page.screenshot(path='c:/resrise-studio/maira_after_continue.png')
    browser.close()
print('Done!')
