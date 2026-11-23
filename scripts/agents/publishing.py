"""Instagram post publishing agent."""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from playwright.sync_api import Page

from ..core.config import get_settings, load_queue, save_queue
from ..core.logging import ActivityLogger, get_logger
from ..core.utils import get_valid_media_paths, RateLimiter
from ..core.browser import BrowserManager, BrowserConfig


def find_create_button(page: Page) -> "object":
    """Locate the Instagram 'Create / Post' button robustly.

    Instagram's nav bar has several spans whose text is 'Post' (the Create
    tooltip, the nav label, etc.). Pick the first one that is actually
    visible so we don't click a hidden decorative element.
    """
    base = (
        "span:has-text('Post'), a:has-text('Post'), div[role='button']:has-text('Post'), "
        "svg[aria-label='New post'], a:has-text('Create'), span:has-text('Create')"
    )
    for cand in page.locator(base).filter(has_text="Post").all():
        try:
            if cand.is_visible(timeout=1500):
                return cand
        except Exception:
            continue
    for cand in page.locator(base).all():
        try:
            if cand.is_visible(timeout=1500):
                return cand
        except Exception:
            continue
    return page.locator(base).first


def select_portrait_crop(page: Page) -> None:
    """Switch Instagram's default 1:1 square crop to 4:5 portrait."""
    try:
        crop_btn = page.locator(
            "button[aria-label*='crop' i], div[role='button'][aria-label*='crop' i], "
            "svg[aria-label*='crop' i], button:has-text('Crop'), div[role='button']:has-text('Crop')"
        ).first
        crop_btn.wait_for(state="visible", timeout=8000)
        crop_btn.click(force=True)
        time.sleep(1.0)

        portrait_opt = page.locator(
            "div[role='radio']:has-text('4:5'), span:has-text('4:5'), button:has-text('4:5')"
        ).first
        portrait_opt.wait_for(state="visible", timeout=5000)
        portrait_opt.click(force=True)
        time.sleep(1.0)
        logger.info("Selected 4:5 portrait crop")
    except Exception as e:
        logger.warning("Could not select 4:5 portrait crop", error=str(e))
        if crop_btn.is_visible(timeout=3000):
            crop_btn.click(force=True)
            time.sleep(1.0)
            portrait_opt = page.locator("span:text-is('4:5'), div[role='button']:has-text('4:5')").first
            if portrait_opt.is_visible(timeout=2000):
                portrait_opt.click(force=True)
                time.sleep(1.0)
    except Exception:
        pass


def run_publishing(account: str, dry_run: bool = False) -> None:
    """Publish approved posts to Instagram."""
    logger = get_logger("resrise.agent.publishing")
    activity_logger = ActivityLogger(
        account,
        log_file=get_settings().project_dir / f"publish_log_{account}.txt",
    )

    queue = load_queue()
    ready_items = [
        item for item in queue
        if item.get("account") == account
        and item.get("status") == "APPROVED"
        and get_valid_media_paths(item.get("media_paths", []))
    ]

    if not ready_items:
        activity_logger.log(
            "No APPROVED posts with valid media_paths found. "
            "Approve posts & attach media in approval dashboard first."
        )
        return

    activity_logger.log(f"Publishing {len(ready_items)} post(s) for @{account} (dry_run={dry_run})")

    # Rate limiter for publishing (1 post per 60 seconds)
    publish_limiter = RateLimiter(rate=1/60, burst=1)

    browser_config = BrowserConfig(
        viewport={"width": 1200, "height": 820},
    )

    with BrowserManager(account, browser_config) as page:
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5.0)

        for item in ready_items:
            media_paths = get_valid_media_paths(item.get("media_paths", []))[:10]
            caption = item["caption"]
            names = ", ".join(Path(m).name for m in media_paths)
            activity_logger.log(f"Publishing draft [id:{item['id']}] ({len(media_paths)} file(s): {names})")

            try:
                publish_limiter.acquire()

                # Click Create button
                create_btn = page.locator(
                    "span:has-text('Post'), a:has-text('Post'), div[role='button']:has-text('Post'), "
                    "svg[aria-label='New post'], a:has-text('Create'), span:has-text('Create')"
                ).first
                create_btn.click(force=True)
                time.sleep(2.5)

                # Upload media files
                file_input = page.locator("input[type='file']").first
                file_input.set_input_files(media_paths)
                time.sleep(4.0)

                # Select portrait crop for 4:5
                select_portrait_crop(page)

                # Click Next twice
                for _ in range(2):
                    next_btn = page.locator("div[role='button']:text-is('Next'), button:text-is('Next')").first
                    if next_btn.is_visible(timeout=5000):
                        next_btn.click(force=True)
                        time.sleep(2.5)

                # Fill caption
                caption_box = page.locator(
                    "div[aria-label='Write a caption...'][role='textbox'], textarea[aria-label='Write a caption...'], "
                    "div[aria-label='Add a caption...'][role='textbox'], [contenteditable='true'][aria-label='Add a caption...'], "
                    "[contenteditable='true'][aria-label='Write a caption...']"
                ).first
                caption_box.click(force=True)
                time.sleep(1.0)
                caption_box.fill(caption)
                time.sleep(2.0)

                if dry_run:
                    activity_logger.log(
                        f"[DRY RUN] Ready to share [id:{item['id']}] ({len(media_paths)} file(s)). "
                        "Skipping Share click."
                    )
                    continue

                # Click Share
                share_btn = page.locator("div[role='button']:text-is('Share'), button:text-is('Share')").first
                share_btn.click(force=True)
                time.sleep(8.0)

                # Update status
                item["status"] = "PUBLISHED"
                item["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_queue(queue)
                activity_logger.success(f"Published [id:{item['id']}] successfully!")

                page.keyboard.press("Escape")
                time.sleep(3.0)

            except Exception as e:
                activity_logger.error(f"Failed to publish [id:{item['id']}]", error=str(e))

    activity_logger.log("Publishing session complete")