"""Playwright browser management for Resrise Studio automation."""
import os
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Generator
from dataclasses import dataclass

from playwright.sync_api import sync_playwright, BrowserContext, Page, Playwright

from .config import get_settings
from .logging import get_logger
from .utils import clean_chrome_locks, get_chrome_profile_dir, validate_account


@dataclass
class BrowserConfig:
    """Configuration for browser launch."""
    headless: bool = False
    channel: str = "chrome"
    viewport: dict = None
    window_position: tuple = (80, 50)
    window_size: tuple = (1200, 800)
    args: list = None

    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1150, "height": 760}
        if self.args is None:
            self.args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                f"--window-position={self.window_position[0]},{self.window_position[1]}",
                f"--window-size={self.window_size[0]},{self.window_size[1]}",
            ]


class BrowserManager:
    """Manages Playwright browser contexts for Instagram automation."""

    def __init__(self, account: str, config: Optional[BrowserConfig] = None):
        self.account = validate_account(account)
        self.config = config or BrowserConfig()
        self.logger = get_logger(f"resrise.browser.{self.account}")
        self._playwright: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    @property
    def profile_dir(self) -> Path:
        """Get Chrome profile directory for this account."""
        return get_chrome_profile_dir(self.account)

    def _get_launch_args(self) -> list:
        """Get Chrome launch arguments."""
        return self.config.args.copy()

    @contextmanager
    def session(self) -> Generator[Page, None, None]:
        """Context manager for a browser session."""
        self._playwright = sync_playwright().start()
        try:
            self._context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                channel=self.config.channel,
                headless=self.config.headless,
                viewport=self.config.viewport,
                args=self._get_launch_args(),
            )

            # Anti-detection script
            self._context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )

            self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
            self.logger.info("Browser session started", profile_dir=str(self.profile_dir))

            yield self._page

        finally:
            self.close()

    def close(self) -> None:
        """Close browser and cleanup."""
        if self._context:
            self._context.close()
            self._context = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self._page = None
        self.logger.info("Browser session closed")

    def __enter__(self) -> Page:
        """Enter context manager (for use without 'with')."""
        self._playwright = sync_playwright().start()
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            channel=self.config.channel,
            headless=self.config.headless,
            viewport=self.config.viewport,
            args=self._get_launch_args(),
        )
        self._context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
        return self._page

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.close()

    @property
    def page(self) -> Page:
        """Get current page."""
        if self._page is None:
            raise RuntimeError("Browser session not started. Use 'with manager.session() as page:'")
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Get current browser context."""
        if self._context is None:
            raise RuntimeError("Browser session not started")
        return self._context

    def wait_for_login(self, timeout: int = 300) -> bool:
        """
        Wait for user to complete login in the browser.

        Returns:
            True if login successful, False if timeout
        """
        import time

        self.logger.info("Waiting for login...", timeout=timeout)
        for _ in range(timeout // 3):
            time.sleep(3.0)
            if not self._page.locator("input[name='username'], input[name='email'], input[type='password']").count():
                if "/accounts/login" not in self._page.url:
                    self.logger.info("Login successful")
                    time.sleep(5.0)
                    return True
        self.logger.warning("Login timeout")
        return False

    def handle_popups(self) -> None:
        """Handle common Instagram popups (Not Now, etc.)."""
        for _ in range(2):
            try:
                not_now = self._page.locator(
                    "button:has-text('Not Now'), div[role='button']:has-text('Not Now')"
                ).first
                if not_now.is_visible(timeout=2000):
                    not_now.click()
                    self.logger.debug("Dismissed popup")
                    time.sleep(1.5)
            except Exception:
                pass


# Convenience function for quick scripts
def open_login_browser(account: str) -> None:
    """Open Chrome for manual Instagram login (used by login.py)."""
    import subprocess

    account = validate_account(account)
    profile_dir = get_chrome_profile_dir(account)
    profile_dir.mkdir(parents=True, exist_ok=True)
    clean_chrome_locks(profile_dir)

    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(local_app_data, r"Google\Chrome\Application\chrome.exe"),
    ]

    chrome_path = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not chrome_path:
        raise RuntimeError("Google Chrome not found in standard locations")

    cmd = [
        chrome_path,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.instagram.com/",
    ]

    print("=" * 60)
    print(f"OPENING CHROME FOR INSTAGRAM LOGIN (@{account})")
    print("=" * 60)
    print(f"Profile: {profile_dir}\n")
    print("1. A Google Chrome window will open to Instagram.")
    print(f"2. Log into @{account} as you normally would.")
    print("3. Once you see your feed, CLOSE that Chrome window completely.")
    print(f"4. Your session is saved for automation scripts.")
    print("=" * 60)

    subprocess.Popen(cmd)
    print(f"\nChrome launched for @{account}! Look for the new Chrome window.")