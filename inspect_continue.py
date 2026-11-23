import sys
sys.path.append('c:/resrise-studio')
from scripts.core.config import get_settings
from playwright.sync_api import sync_playwright

settings = get_settings()
user_data_dir = settings.get_chrome_profile_dir('mairamehraofficial')

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        channel='chrome'
    )
    page = browser.new_page()
    page.goto('https://www.instagram.com/', wait_until='domcontentloaded')
    page.wait_for_timeout(3000)
    
    # Check buttons and links
    buttons = page.locator('button, div[role="button"], a').all()
    print('Total buttons/links:', len(buttons))
    for b in buttons:
        txt = b.inner_text().strip()
        if txt in ['Continue', 'Use another profile', 'Create new account']:
            print('MATCH:', b.evaluate('el => el.tagName'), 'text:', txt, 'classes:', b.get_attribute('class'))
            # Click it!
            if txt == 'Continue':
                print('Clicking Continue!')
                b.click(force=True)
                page.wait_for_timeout(5000)
                print('After click URL:', page.url)
                page.screenshot(path='c:/resrise-studio/maira_after_click_continue.png')
                break
    browser.close()
print('Inspection complete!')
