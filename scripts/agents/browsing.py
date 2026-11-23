"""Vision-aware Instagram feed browsing & commenting agent."""
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Set

from playwright.sync_api import Page

from ..core.config import get_settings, load_config
from ..core.logging import ActivityLogger, get_logger
from ..core.utils import RateLimiter
from ..core.vision import VisionClient
from ..core.browser import BrowserManager, BrowserConfig


@dataclass
class BrowsingConfig:
    """Configuration for browsing behavior."""
    max_batches: int = 8
    batch_size: int = 4
    cooldown_seconds: int = 240
    draft_only: bool = False
    max_posts_per_batch: int = 4


class VisionCommentAgent:
    """Inspects post photo + caption using vision LLM to generate contextual comments."""

    PERSONA_BRIEFS = {
        "avanyamehra": "Avanya Mehra, a poised high-fashion & editorial model (warm, refined, concise).",
        "mairamehraofficial": "Maira Mehra, a warm style & travel lifestyle creator (friendly, observant, natural).",
        "iamgagankumar": "Gagan Kumar, a menswear & grooming creator (sharp, respectful, authentic).",
        "resrise": "Resrise Studio, creative production agency & AI creator incubator (visionary, polished, direct).",
        "gagankumarrocks": "Gagan Kumar Rocks, agency founder & creator systems architect (strategic, insightful, high-signal).",
    }

    def __init__(self, vision_client: VisionClient):
        self.vision_client = vision_client
        self.logger = get_logger("resrise.agent.browsing")

    def generate_comment(
        self,
        account: str,
        image_bytes: bytes,
        caption_text: str,
        creator_handle: str,
    ) -> str:
        persona = self.PERSONA_BRIEFS[account]
        prompt = (
            f"You are replying on Instagram as @{account} ({persona}).\n"
            f"Creator handle: {creator_handle or 'unknown'}\n"
            f"Post caption: {caption_text[:400] if caption_text else 'none'}\n\n"
            "Look carefully at the attached post screenshot.\n"
            "Rules:\n"
            "1. Only comment on what is actually visible in the photo and caption (never assume gender, menswear, or saree if not shown).\n"
            "2. Keep it natural, specific, and concise (5 to 14 words, max 1 emoji, no hashtags).\n"
            "3. If the post is an ad, meme, news/tragedy, political, or unclear, reply with exactly: SKIP"
        )
        reply = self.vision_client.call_vision(prompt, image_bytes)
        return reply or ""


def extract_creator_username(page: Page) -> str:
    """Extract creator username from post page."""
    try:
        return page.evaluate("""() => {
            const headerLink = document.querySelector('header a[role="link"], article a[role="link"]');
            if (headerLink) {
                const parts = headerLink.pathname.split('/').filter(Boolean);
                if (parts.length > 0) return '@' + parts[0];
            }
            return '';
        }""")
    except Exception:
        return ""


def extract_caption_text(page: Page) -> str:
    """Extract caption text from post page."""
    try:
        return page.evaluate("""() => {
            const h1 = document.querySelector('h1');
            if (h1 && h1.innerText.trim()) return h1.innerText.trim();
            const span = document.querySelector("article ul span, div[role='dialog'] ul span");
            return span ? span.innerText.trim() : '';
        }""")
    except Exception:
        return ""


def take_post_screenshot(page: Page) -> bytes:
    """Take screenshot of the post."""
    try:
        return page.locator("article").first.screenshot()
    except Exception:
        return page.screenshot()


def like_post(page: Page) -> bool:
    """Like the current post."""
    try:
        page.evaluate("""() => {
            const svgs = Array.from(document.querySelectorAll('svg'));
            for (const svg of svgs) {
                const label = (svg.getAttribute('aria-label') || '').toLowerCase();
                const rect = svg.getBoundingClientRect();
                if (label === 'like' && rect.width >= 18) {
                    const btn = svg.closest('button') || svg.closest('div[role="button"]');
                    if (btn) { btn.click(); break; }
                }
            }
        }""")
        time.sleep(random.uniform(2.5, 4.0))
        return True
    except Exception:
        return False


def post_comment(page: Page, comment_text: str) -> bool:
    """Post a comment on the current post."""
    try:
        comment_box = page.locator(
            "textarea[placeholder*='comment' i], "
            "textarea[aria-label*='comment' i], "
            "div[role='textbox'][aria-label*='comment' i], "
            "form textarea"
        ).first

        if comment_box.is_visible(timeout=3000):
            comment_box.click(force=True)
            time.sleep(1.0)
            comment_box.press_sequentially(comment_text, delay=random.randint(70, 120))
            time.sleep(random.uniform(1.5, 2.5))

            post_btn = page.locator("div[role='button']:text-is('Post'), button:text-is('Post')").first
            if post_btn.is_visible(timeout=2000):
                post_btn.click(force=True)
            else:
                page.keyboard.press("Enter")
            return True
    except Exception:
        pass
    return False


def collect_post_urls(page: Page, account: str, processed: Set[str], target_count: int) -> list:
    """Scroll feed and collect post URLs."""
    collected = []
    scroll_tries = 0

    while len(collected) < target_count and scroll_tries < 15:
        hrefs = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            return links.map(a => a.href).filter(href => href && (href.includes('/p/') || href.includes('/reel/')));
        }""")

        for url in hrefs:
            clean_url = url.split("?")[0]
            if "/liked_by/" in clean_url or "/comments/" in clean_url or "/tag/" in clean_url:
                continue
            if account in clean_url.lower():
                continue
            if clean_url not in processed and clean_url not in collected:
                collected.append(clean_url)
                if len(collected) >= target_count:
                    break

        if len(collected) >= target_count:
            break

        page.mouse.move(600, 400)
        page.mouse.wheel(0, 800)
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(random.uniform(3.5, 5.0))
        scroll_tries += 1

    return collected


def save_comment_draft(account: str, post_url: str, comment_text: str) -> None:
    """Save comment draft to JSON file."""
    import json
    from datetime import datetime

    settings = get_settings()
    draft_path = settings.project_dir / f"comment_drafts_{account}.json"
    drafts = []
    if draft_path.exists():
        try:
            with open(draft_path, "r", encoding="utf-8") as f:
                drafts = json.load(f)
        except Exception:
            drafts = []

    drafts.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "post_url": post_url,
        "suggested_comment": comment_text,
    })
    with open(draft_path, "w", encoding="utf-8") as f:
        json.dump(drafts, f, indent=2, ensure_ascii=False)


def log_posted_comment(account: str, batch_num: int, post_url: str, creator: str, comment_text: str) -> None:
    """Log posted comment to review file."""
    settings = get_settings()
    review_log_path = settings.project_dir / f"comments_review_{account}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [Batch #{batch_num}] [@{account}] -> {creator or 'unknown'} | {post_url} | Comment: {comment_text}\n"
    try:
        with open(review_log_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        get_logger("resrise.agent.browsing").error("Failed to write review log", error=str(e))


def run_browsing(account: str, config: Optional[BrowsingConfig] = None) -> None:
    """Run vision-aware feed browsing for an account."""
    config = config or BrowsingConfig()
    logger = get_logger("resrise.agent.browsing")
    activity_logger = ActivityLogger(
        account,
        log_file=get_settings().project_dir / f"activity_log_{account}.txt",
    )

    settings = get_settings()
    vision_client = VisionClient()

    # Log which provider we're using
    available = vision_client.get_available_providers()
    if available:
        activity_logger.log(f"Using vision providers: {', '.join(available)}")
    else:
        activity_logger.log(
            "⚠️ No vision providers configured. Set OPENROUTER_API_KEY in .env, "
            "start OmniRoute (port 20128), set GEMINI_API_KEY, or start Ollama."
        )
        return

    agent = VisionCommentAgent(vision_client)
    processed_urls: Set[str] = set()
    batch_count = 1

    # Rate limiter for Instagram actions (1 action per 30 seconds)
    action_limiter = RateLimiter(rate=1/30, burst=1)

    browser_config = BrowserConfig(
        viewport={"width": 1150, "height": 760},
        window_size=(1200, 800),
    )

    with BrowserManager(account, browser_config) as page:
        # Navigate to Instagram
        try:
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
        except Exception:
            activity_logger.log("Initial navigation stabilizing...")

        time.sleep(6.0)

        # Check login
        has_login = page.locator("input[name='username'], input[name='email'], input[type='password']").count() > 0
        if has_login or "/accounts/login" in page.url:
            activity_logger.log(
                f"⚠️ Not logged in. Please log into @{account} in the Chrome window "
                f"(or run login.py --account {account})..."
            )
            # Wait for login
            for _ in range(120):
                time.sleep(3.0)
                if (
                    not page.locator("input[name='username'], input[name='email'], input[type='password']").count()
                    and "/accounts/login" not in page.url
                ):
                    activity_logger.log("✅ Login successful! Stabilizing...")
                    time.sleep(5.0)
                    break
        else:
            activity_logger.log("✅ Logged in successfully!")

        # Clean up environment variables that interfere with Playwright
        for env_key in list(os.environ.keys()):
            if any(kw in env_key.upper() for kw in ["PLAYWRIGHT", "BROWSER", "CDP"]):
                os.environ.pop(env_key, None)

        while True:
            activity_logger.log(
                f"--- Starting Vision Feed Batch #{batch_count} (Target: {config.batch_size} posts) ---"
            )

            try:
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
            except Exception:
                pass

            time.sleep(random.uniform(3.5, 5.5))

            # Handle popups
            for _ in range(2):
                try:
                    not_now = page.locator(
                        "button:has-text('Not Now'), div[role='button']:has-text('Not Now')"
                    ).first
                    if not_now.is_visible(timeout=2000):
                        not_now.click()
                        time.sleep(1.5)
                except Exception:
                    pass

            # Collect post URLs
            activity_logger.log("Scrolling main feed to collect posts...")
            collected_urls = collect_post_urls(page, account, processed_urls, config.batch_size)

            for idx, post_url in enumerate(collected_urls, start=1):
                try:
                    processed_urls.add(post_url)
                    activity_logger.log(f"[{idx}/{len(collected_urls)}] Inspecting post: {post_url}")

                    action_limiter.acquire()
                    page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(random.uniform(3.5, 5.5))

                    creator_username = extract_creator_username(page)

                    # Skip own posts
                    if creator_username.lstrip("@").lower() == account:
                        activity_logger.log(f"Post #{idx}: Own post detected, skipping.")
                        continue

                    caption_text = extract_caption_text(page)
                    img_bytes = take_post_screenshot(page)

                    comment_text = agent.generate_comment(
                        account, img_bytes, caption_text, creator_username
                    )

                    if not comment_text:
                        activity_logger.log(f"Post #{idx}: Vision agent returned SKIP. Skipping.")
                        continue

                    if config.draft_only:
                        save_comment_draft(account, post_url, comment_text)
                        activity_logger.log(f"Post #{idx}: Saved draft -> '{comment_text}'")
                        continue

                    # Like + post comment
                    if like_post(page):
                        activity_logger.log(f"Post #{idx}: Liked post")

                    action_limiter.acquire()
                    if post_comment(page, comment_text):
                        activity_logger.log(f"Post #{idx}: Posted comment -> '{comment_text}'")
                        log_posted_comment(account, batch_count, post_url, creator_username, comment_text)
                        time.sleep(random.uniform(8.0, 14.0))
                    else:
                        activity_logger.log(f"Post #{idx}: Comment box unavailable.")

                except Exception as e:
                    activity_logger.log(f"Skipped Post #{idx} due to error: {e}")

            if config.max_batches > 0 and batch_count >= config.max_batches:
                activity_logger.log(
                    f"✅ Completed {config.max_batches} batches. "
                    f"Review posted comments in: comments_review_{account}.txt"
                )
                break

            activity_logger.log(f"Batch #{batch_count} completed. Cooling down {config.cooldown_seconds}s...")
            time.sleep(config.cooldown_seconds + random.uniform(5.0, 15.0))
            batch_count += 1


# Import os at module level for the env cleanup
import os