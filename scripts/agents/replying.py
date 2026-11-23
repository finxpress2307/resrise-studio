"""Vision-aware Instagram comment reply agent."""
import hashlib
import json
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, Tuple

from playwright.sync_api import Page

from ..core.config import get_settings, load_config
from ..core.logging import ActivityLogger, get_logger
from ..core.utils import RateLimiter
from ..core.vision import VisionClient
from ..core.browser import BrowserManager, BrowserConfig


class VisionReplyAgent:
    """Generates contextual replies to comments on own posts using vision LLM."""

    PERSONA_BRIEFS = {
        "avanyamehra": "Avanya Mehra, a poised high-fashion & editorial model (warm, refined, concise).",
        "mairamehraofficial": "Maira Mehra, a warm style & travel lifestyle creator (friendly, appreciative, natural).",
        "iamgagankumar": "Gagan Kumar, a menswear & grooming creator (sharp, respectful, authentic).",
        "resrise": "Resrise Studio, creative production agency & AI creator incubator (visionary, polished, direct).",
        "gagankumarrocks": "Gagan Kumar Rocks, agency founder & creator systems architect (strategic, insightful, high-signal).",
    }

    def __init__(self, vision_client: VisionClient):
        self.vision_client = vision_client
        self.logger = get_logger("resrise.agent.replying")

    def generate_reply(
        self,
        account: str,
        image_bytes: bytes,
        caption_text: str,
        incoming_comment: str,
    ) -> str:
        persona = self.PERSONA_BRIEFS[account]
        prompt = (
            f"You are @{account} ({persona}) replying to a comment on your own Instagram post.\n"
            f"Your post caption: {caption_text[:400] if caption_text else 'none'}\n"
            f"Incoming comment to reply to:\n{incoming_comment[:300]}\n\n"
            "Look at the attached post screenshot, the caption, and the incoming comment.\n"
            "Rules:\n"
            "1. Write a natural, warm, context-specific reply (4 to 14 words, max 1 emoji, no hashtags).\n"
            "2. Directly acknowledge what they actually said or asked, matching what is in the photo.\n"
            "3. If the comment is spam, bot promo ('DM us', 'promote on'), hate, or unclear, reply with exactly: SKIP"
        )
        reply = self.vision_client.call_vision(prompt, image_bytes)
        return reply or ""


def extract_comment_parts(row) -> Tuple[str, str]:
    """Extract (author_handle, clean_comment_body) without volatile timestamps/UI labels."""
    try:
        data = row.evaluate("""(el) => {
            const authorLink = el.querySelector('a[role="link"][href^="/"]');
            const author = authorLink ? authorLink.pathname.replace(/\\//g, '').toLowerCase() : '';
            const spans = Array.from(el.querySelectorAll('span'))
                .map(s => s.innerText.trim())
                .filter(t => t && t.toLowerCase() !== author);
            return { author, body: spans.join(' ') };
        }""")
        author = data.get("author", "").strip()
        body = data.get("body", "").strip()
    except Exception:
        author = ""
        body = row.inner_text().strip()

    # Strip volatile relative timestamps (e.g., 5m, 2h, 3d, 1w) and Instagram action labels
    body = re.sub(r"\b\d+\s*[smhdw]\b", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\b(Reply|Like|Likes|\d+\s+likes?|View replies.*|Hide replies)\b", "", body, flags=re.IGNORECASE)
    normalized = " ".join(body.split())
    return author, normalized


def hash_comment(author: str, clean_body: str) -> str:
    """Generate hash for comment deduplication."""
    key = f"{author.lower()}:{' '.join(clean_body.strip().split())}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def load_replied_cache(cache_file: Path, logger) -> Set[str]:
    """Load replied comments cache from file."""
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            logger.warning(f"Could not load cache file: {e}")
    return set()


def save_replied_cache(cache_file: Path, cache_set: Set[str], logger) -> None:
    """Save replied comments cache to file."""
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(list(cache_set), f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save cache file: {e}")


def run_replying(account: str) -> None:
    """Run vision-aware comment replying for an account."""
    logger = get_logger("resrise.agent.replying")
    activity_logger = ActivityLogger(
        account,
        log_file=get_settings().project_dir / f"reply_activity_log_{account}.txt",
    )

    settings = get_settings()
    vision_client = VisionClient()

    available = vision_client.get_available_providers()
    if available:
        activity_logger.log(f"Using vision providers: {', '.join(available)}")
    else:
        activity_logger.log(
            "⚠️ No vision providers configured. Set OPENROUTER_API_KEY in .env, "
            "start OmniRoute (port 20128), set GEMINI_API_KEY, or start Ollama."
        )
        return

    agent = VisionReplyAgent(vision_client)
    cache_file = settings.project_dir / f"replied_comments_cache_{account}.json"
    profile_url = f"https://www.instagram.com/{account}/"

    replied_comments_cache = load_replied_cache(cache_file, logger)
    activity_logger.log(f"Loaded {len(replied_comments_cache)} previously replied comment signatures from cache.")

    # Rate limiter for replies (1 reply per 45 seconds)
    reply_limiter = RateLimiter(rate=1/45, burst=1)

    browser_config = BrowserConfig(
        viewport={"width": 1150, "height": 760},
        window_size=(1200, 800),
    )

    with BrowserManager(account, browser_config) as page:
        # Navigate to profile
        activity_logger.log(f"Navigating to {profile_url} to check comments...")
        try:
            page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as nav_err:
            activity_logger.log(f"Initial navigation stabilizing ({nav_err})...")
        time.sleep(6.0)

        # Check login
        has_login = page.locator("input[name='username'], input[name='email'], input[type='password']").count() > 0
        if has_login or "/accounts/login" in page.url:
            activity_logger.log(
                f"⚠️ Not logged in. Please log into @{account} in the Chrome window "
                f"(or run login.py --account {account})..."
            )
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
            activity_logger.log("✅ Session active!")

        # Clean up environment variables
        for env_key in list(os.environ.keys()):
            if any(kw in env_key.upper() for kw in ["PLAYWRIGHT", "BROWSER", "CDP"]):
                os.environ.pop(env_key, None)

        batch_count = 1
        posts_to_check = 5

        while True:
            activity_logger.log(f"--- Starting Vision Reply Batch #{batch_count} ---")
            try:
                page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
            except Exception as nav_err:
                activity_logger.log(f"Navigation warning: {nav_err}. Retrying next cycle...")
                time.sleep(10.0)
                continue
            time.sleep(random.uniform(5.0, 8.0))

            posts = page.locator("a[href*='/p/'], a[href*='/reel/']").all()

            for i in range(min(posts_to_check, len(posts))):
                try:
                    target_post = posts[i]
                    target_post.scroll_into_view_if_needed()
                    time.sleep(1.0)
                    target_post.click(force=True)
                    activity_logger.log(f"Opened post #{i + 1} to inspect photo, caption & comments...")
                    time.sleep(random.uniform(5.0, 7.0))

                    # Extract caption
                    caption_text = page.evaluate("""() => {
                        const h1 = document.querySelector('h1');
                        if (h1 && h1.innerText.trim()) return h1.innerText.trim();
                        const firstSpan = document.querySelector("div[role='dialog'] ul span, article ul span");
                        return firstSpan ? firstSpan.innerText.trim() : '';
                    }""")

                    # Take screenshot
                    try:
                        img_bytes = page.locator("div[role='dialog'], article").first.screenshot()
                    except Exception:
                        img_bytes = page.screenshot()

                    # Find comments
                    comment_container = page.locator("div[role='dialog'] ul, main ul").first
                    if comment_container.is_visible():
                        comment_container.evaluate("el => el.scrollTop = 200")
                        time.sleep(1.5)

                    comment_rows = page.locator("div[role='dialog'] ul > div, div[role='dialog'] ul li, main ul li").all()
                    replied_in_post = 0

                    for row in comment_rows:
                        if replied_in_post >= 2:
                            break

                        try:
                            author, clean_body = extract_comment_parts(row)
                            if not clean_body:
                                continue

                            # Skip own comments
                            if author == account.lower():
                                continue

                            comment_id = hash_comment(author, clean_body)
                            if comment_id in replied_comments_cache:
                                continue

                            reply_btn = row.locator("button:has-text('Reply'), span:has-text('Reply')").first
                            if not reply_btn.is_visible(timeout=1500):
                                continue

                            comment_for_ai = f"@{author}: {clean_body}" if author else clean_body
                            reply_text = agent.generate_reply(
                                account, img_bytes, caption_text, comment_for_ai
                            )

                            if not reply_text:
                                activity_logger.log(f"Skipped comment [id:{comment_id}] (Vision agent returned SKIP).")
                                replied_comments_cache.add(comment_id)
                                save_replied_cache(cache_file, replied_comments_cache, logger)
                                continue

                            reply_limiter.acquire()
                            reply_btn.click(force=True)
                            time.sleep(1.5)

                            reply_box = page.locator(
                                "textarea[placeholder*='Reply' i], "
                                "textarea[aria-label*='Reply' i], "
                                "div[role='textbox'][aria-label*='Reply' i]"
                            ).last
                            if reply_box.is_visible(timeout=3000):
                                reply_box.click(force=True)
                                time.sleep(0.8)

                                reply_box.press_sequentially(reply_text, delay=random.randint(60, 110))
                                time.sleep(random.uniform(1.2, 2.0))

                                submit_btn = page.locator("div[role='button']:text-is('Reply'), button:text-is('Reply')").last
                                if submit_btn.is_visible(timeout=2000):
                                    submit_btn.click(force=True)
                                else:
                                    page.keyboard.press("Enter")

                                replied_comments_cache.add(comment_id)
                                save_replied_cache(cache_file, replied_comments_cache, logger)

                                activity_logger.log(f"✅ Vision reply [id:{comment_id}]: '{reply_text}'")
                                replied_in_post += 1
                                time.sleep(random.uniform(5.0, 8.0))

                        except Exception as row_err:
                            activity_logger.log(f"Row inspection note on post #{i + 1}: {row_err}")
                            continue

                    if replied_in_post == 0:
                        activity_logger.log(f"No new unreplied comments found on post #{i + 1}.")

                    page.keyboard.press("Escape")
                    time.sleep(random.uniform(2.0, 4.0))

                except Exception as e:
                    activity_logger.log(f"Error checking post #{i + 1}: {e}")
                    page.keyboard.press("Escape")

            activity_logger.log(f"Batch #{batch_count} reply check completed. Waiting 3 minutes...")
            time.sleep(180 + random.uniform(5.0, 15.0))
            batch_count += 1


import os