import sys
sys.path.append('c:/resrise-studio')
from scripts.core.config import get_settings
from playwright.sync_api import sync_playwright

settings = get_settings()

accounts = ['avanyamehra', 'iamgagankumar', 'gagankumarrocks', 'resrise']
results = {}

with sync_playwright() as p:
    for acc in accounts:
        user_data_dir = settings.get_chrome_profile_dir(acc)
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=True,
                channel='chrome'
            )
            page = browser.new_page()
            page.goto('https://www.instagram.com/', wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(2000)
            is_logged_in = page.locator('svg[aria-label="Home"]').count() > 0 or page.locator(f'a[href="/{acc}/"]').count() > 0
            results[acc] = {'logged_in': is_logged_in, 'url': page.url}
            page.screenshot(path=f'c:/resrise-studio/{acc}_login_check.png')
            browser.close()
        except Exception as e:
            results[acc] = {'error': str(e)}

print(results)
