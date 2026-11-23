import argparse
import base64
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.request
from datetime import datetime
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from ig_browsing import PERSONA_BRIEFS, get_openrouter_config, is_openrouter_configured, call_vision_model
from ig_replier import extract_comment_parts, hash_comment, load_replied_cache, save_replied_cache, VisionReplyAgent, is_already_responded

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


def get_chrome_profile_dir(account: str) -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    return os.path.join(local_app_data, "Google", "Chrome", "User Data - Automation", account)


def log_activity(log_file_path: str, account: str, message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [@{account}] {message}"
    print(log_msg, flush=True)
    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")


def reply_to_post_comments(account: str, post_url: str, max_replies: int = 15) -> int:
    log_file_path = os.path.join(PROJECT_DIR, f"reply_activity_log_{account}.txt")
    cache_file = os.path.join(PROJECT_DIR, f"replied_comments_cache_{account}.json")

    user_data_dir = get_chrome_profile_dir(account)
    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lock_path = os.path.join(user_data_dir, lock_file)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    replied_cache = load_replied_cache(cache_file, log_file_path, account)
    log_activity(log_file_path, account, f"Loaded {len(replied_cache)} cached replied comments.")
    log_activity(log_file_path, account, f"Opening post: {post_url}...")

    total_replied = 0

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            viewport={"width": 1200, "height": 850},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5.0)

        # Extract caption
        caption_text = page.evaluate("""() => {
            const h1 = document.querySelector('h1');
            if (h1 && h1.innerText.trim()) return h1.innerText.trim();
            const firstSpan = document.querySelector("article ul span, div[role='dialog'] ul span");
            return firstSpan ? firstSpan.innerText.trim() : '';
        }""")
        log_activity(log_file_path, account, f"Post caption: '{caption_text[:100]}...'")

        # Screenshot post image for vision agent
        try:
            img_bytes = page.locator("article, div[role='dialog']").first.screenshot()
        except Exception:
            img_bytes = page.screenshot()

        # Scroll comment list to load all comments
        log_activity(log_file_path, account, "Loading comments list...")
        for _ in range(3):
            page.evaluate("""() => {
                const containers = document.querySelectorAll("ul, div[style*='overflow']");
                containers.forEach(c => c.scrollTop += 500);
            }""")
            time.sleep(1.5)

        # Locate all comment reply buttons
        reply_buttons = page.locator("span:text-is('Reply')").all()
        log_activity(log_file_path, account, f"Found {len(reply_buttons)} 'Reply' buttons on post.")

        for idx, reply_btn in enumerate(reply_buttons):
            if total_replied >= max_replies:
                break

            try:
                if not reply_btn.is_visible(timeout=1500):
                    continue

                # Locate enclosing comment container
                comment_card = reply_btn.locator("xpath=ancestor::li[1]").first
                if not comment_card.is_visible(timeout=500):
                    comment_card = reply_btn.locator("xpath=ancestor::div[.//h3 or .//a[@role='link']][1]").first

                row_text = comment_card.inner_text().strip() if comment_card.is_visible(timeout=500) else ""

                # Extract author
                author = ""
                if comment_card.is_visible(timeout=500):
                    author_el = comment_card.locator("h3, a[role='link']").first
                    if author_el.is_visible(timeout=500):
                        author = author_el.inner_text().strip().lower().lstrip("@")

                # Skip own comments
                if author and author == account.lower():
                    continue

                # Skip if already replied or user already responded
                if is_already_responded(comment_card, account, page):
                    log_activity(log_file_path, account, f"Comment from @{author} already has a response from @{account}. Skipping.")
                    replied_cache.add(hash_comment(author, row_text))
                    save_replied_cache(cache_file, replied_cache, log_file_path, account)
                    continue

                comment_id = hash_comment(author, row_text)
                if comment_id in replied_cache:
                    continue

                # Clean incoming comment text
                clean_comment = row_text
                if author and clean_comment.lower().startswith(author):
                    clean_comment = clean_comment[len(author):].strip()
                clean_comment = re.sub(r"\b\d+\s*[smhdw]\b", "", clean_comment, flags=re.IGNORECASE)
                clean_comment = re.sub(r"\b(Reply|Like|Likes|\d+\s+likes?|View replies.*|Hide replies)\b", "", clean_comment, flags=re.IGNORECASE).strip()

                incoming_for_ai = f"@{author}: {clean_comment}" if author else clean_comment

                log_activity(log_file_path, account, f"Generating AI reply for [{idx+1}/{len(reply_buttons)}] @{author}: '{clean_comment[:60]}'...")
                reply_text = VisionReplyAgent.generate_reply(account, img_bytes, caption_text, incoming_for_ai)

                if not reply_text:
                    log_activity(log_file_path, account, f"Vision model returned SKIP for @{author}. Caching.")
                    replied_cache.add(comment_id)
                    save_replied_cache(cache_file, replied_cache, log_file_path, account)
                    continue

                # Click reply button
                reply_btn.scroll_into_view_if_needed()
                time.sleep(0.5)
                reply_btn.click(force=True)
                time.sleep(1.2)

                # Locate active visible reply box
                reply_box = page.locator("textarea:visible, [role='textbox']:visible").last
                if not reply_box.is_visible(timeout=3000):
                    reply_box = page.locator("form textarea, textarea[placeholder*='comment' i]").first

                if reply_box.is_visible(timeout=3000):
                    reply_box.click(force=True)
                    time.sleep(0.5)
                    page.keyboard.press("End")
                    time.sleep(0.3)
                    reply_box.press_sequentially(reply_text, delay=random.randint(40, 75))
                    time.sleep(1.0)

                    submit_btn = page.locator(
                        "div[role='button']:text-is('Post'), button:text-is('Post'), "
                        "div[role='button']:text-is('Reply'), button:text-is('Reply')"
                    ).last

                    if submit_btn.is_visible(timeout=2500):
                        submit_btn.click(force=True)
                    else:
                        page.keyboard.press("Enter")

                    replied_cache.add(comment_id)
                    save_replied_cache(cache_file, replied_cache, log_file_path, account)
                    total_replied += 1
                    log_activity(log_file_path, account, f"✅ Replied to @{author}: '{reply_text}'")
                    time.sleep(random.uniform(4.0, 7.0))
                else:
                    log_activity(log_file_path, account, f"⚠️ Reply box not visible for @{author}")

            except Exception as e:
                log_activity(log_file_path, account, f"Error replying to comment #{idx+1}: {e}")

        context.close()

    log_activity(log_file_path, account, f"Finished replying to post comments! Total replied: {total_replied}")
    return total_replied


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reply to comments on a specific Instagram post using AI Vision")
    parser.add_argument("--account", default="avanyamehra", help="Instagram handle")
    parser.add_argument("--url", default="https://www.instagram.com/avanyamehra/p/Df4rjQ-l3Gn/", help="Post URL to reply to")
    parser.add_argument("--max", type=int, default=15, help="Maximum comments to reply to")
    args = parser.parse_args()

    reply_to_post_comments(args.account, args.url, args.max)
