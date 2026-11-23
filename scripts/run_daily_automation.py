import argparse
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from ig_browsing import VisionCommentAgent, is_openrouter_configured

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [PIPELINE] {msg}", flush=True)


def get_chrome_profile_dir(account: str) -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    return os.path.join(local_app_data, "Google", "Chrome", "User Data - Automation", account)


def run_story_automation(account: str, max_stories: int = 5) -> None:
    """Watch stories from top tray and send vision-analyzed appreciative replies/reactions."""
    log(f"Starting Story interaction for @{account} (up to {max_stories} stories)...")
    user_data_dir = get_chrome_profile_dir(account)

    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lock_path = os.path.join(user_data_dir, lock_file)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                channel="chrome",
                headless=False,
                viewport={"width": 1200, "height": 820},
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5.0)

            # Dismiss notification popups if any
            for _ in range(2):
                try:
                    not_now = page.locator("button:has-text('Not Now'), div[role='button']:has-text('Not Now')").first
                    if not_now.is_visible(timeout=2000):
                        not_now.click()
                        time.sleep(1.0)
                except Exception:
                    pass

            # Find active story rings (drawn with canvas elements)
            canvases = page.locator("canvas").all()
            log(f"Found {len(canvases)} active story rings on feed.")

            replied_count = 0
            liked_count = 0

            for idx in range(min(max_stories, len(canvases))):
                try:
                    current_canvases = page.locator("canvas").all()
                    if idx >= len(current_canvases):
                        break

                    c = current_canvases[idx]
                    parent_btn = c.locator("xpath=ancestor::div[@role='button'] | ancestor::button").first
                    if not parent_btn.is_visible(timeout=2000):
                        continue

                    user_name = parent_btn.inner_text().strip() or f"story #{idx + 1}"
                    log(f"Viewing story from: {user_name}")
                    parent_btn.click(force=True)
                    time.sleep(3.5)

                    # Screenshot current story frame for vision analysis
                    try:
                        img_bytes = page.locator("section").first.screenshot()
                    except Exception:
                        img_bytes = page.screenshot()

                    # Extract username from story header if available
                    creator_handle = page.evaluate("""() => {
                        const link = document.querySelector('header a[role="link"], header a');
                        if (link) {
                            const name = link.innerText.trim();
                            if (name) return name;
                        }
                        return '';
                    }""") or user_name

                    # Generate vision-analyzed comment
                    comment_text = VisionCommentAgent.generate_comment(
                        account, img_bytes, "", creator_handle
                    )

                    # Look for story reply box
                    reply_input = page.locator(
                        "textarea[placeholder*='Reply' i], textarea[placeholder*='Send' i], "
                        "input[placeholder*='Reply' i], input[placeholder*='Send' i]"
                    ).first

                    if comment_text and reply_input.is_visible(timeout=2500):
                        reply_input.click(force=True)
                        time.sleep(0.5)
                        reply_input.fill(comment_text)
                        time.sleep(0.5)
                        page.keyboard.press("Enter")
                        log(f"✅ Replied to story from {creator_handle}: '{comment_text}'")
                        replied_count += 1
                        time.sleep(2.5)
                    else:
                        if not comment_text:
                            log(f"Story from {creator_handle}: Vision returned SKIP or ad/unclear.")

                    # Like the story if like button is available
                    like_btn = page.locator("svg[aria-label='Like']").first
                    if like_btn.is_visible(timeout=1500):
                        like_btn.click(force=True)
                        log(f"❤️ Liked story from {creator_handle}")
                        liked_count += 1
                        time.sleep(1.5)

                    # Close story viewer
                    page.keyboard.press("Escape")
                    time.sleep(2.0)

                except Exception as se:
                    log(f"Note on story #{idx + 1}: {se}")
                    try:
                        page.keyboard.press("Escape")
                        time.sleep(1.0)
                    except Exception:
                        pass

            context.close()
            log(f"Completed Story interaction for @{account} ({replied_count} replies, {liked_count} likes).")
    except Exception as e:
        log(f"Story interaction error for @{account}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Full Instagram Automation Pipeline: Schedule -> Feed -> Stories -> Comments")
    parser.add_argument("--skip-schedule", action="store_true", help="Skip scheduling step")
    parser.add_argument("--skip-feed", action="store_true", help="Skip feed browsing step")
    parser.add_argument("--skip-stories", action="store_true", help="Skip story interaction step")
    parser.add_argument("--skip-replies", action="store_true", help="Skip post comments reply step")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--feed-posts", type=int, default=3, help="Number of feed posts to analyze/comment per account")
    parser.add_argument("--story-count", type=int, default=4, help="Number of stories to inspect per account")
    args = parser.parse_args()

    log("=" * 60)
    log("STARTING FULL INSTAGRAM AUTOMATION PIPELINE")
    log("=" * 60)

    # 1. Content Scheduling
    if not args.skip_schedule:
        log("\n>>> PHASE 1: SCHEDULING ALL APPROVED POSTS ACROSS ALL ACCOUNTS <<<")
        publisher_py = os.path.join(SCRIPT_DIR, "ig_publisher.py")
        cmd = [sys.executable, publisher_py, "--account", "all", "--schedule"]
        if args.dry_run:
            cmd.append("--dry-run")
        subprocess.run(cmd)
        log("Phase 1 (Scheduling) completed.\n")
    else:
        log("Phase 1 (Scheduling) skipped.\n")

    # 2. Main Feed Auto-Responding (Vision Analysis / Liking / Commenting)
    if not args.skip_feed:
        log(">>> PHASE 2: AUTO-RESPONDING TO MAIN FEED POSTS VIA VISION <<<")
        browsing_py = os.path.join(SCRIPT_DIR, "ig_browsing.py")
        for acc in ACCOUNTS:
            log(f"Running feed vision browsing/auto-response for @{acc} (batch size: {args.feed_posts})...")
            cmd = [sys.executable, browsing_py, "--account", acc, "--max-batches", "1", "--batch-size", str(args.feed_posts)]
            subprocess.run(cmd)
            time.sleep(5.0)
        log("Phase 2 (Feed auto-response) completed.\n")
    else:
        log("Phase 2 (Feed auto-response) skipped.\n")

    # 3. Responding to Stories (Top Tray)
    if not args.skip_stories:
        log(">>> PHASE 3: RESPONDING TO STORIES (TOP TRAY) VIA VISION <<<")
        for acc in ACCOUNTS:
            run_story_automation(acc, max_stories=args.story_count)
            time.sleep(5.0)
        log("Phase 3 (Story interactions) completed.\n")
    else:
        log("Phase 3 (Story interactions) skipped.\n")

    # 4. Responding to Unreplied Comments on Posts
    if not args.skip_replies:
        log(">>> PHASE 4: RESPONDING TO UNREPLIED COMMENTS ON OWN POSTS VIA VISION <<<")
        replier_py = os.path.join(SCRIPT_DIR, "ig_replier.py")
        for acc in ACCOUNTS:
            log(f"Running comment reply check for @{acc}...")
            cmd = [sys.executable, replier_py, "--account", acc]
            proc = subprocess.Popen(cmd)
            start_t = time.time()
            try:
                while time.time() - start_t < 180:
                    if proc.poll() is not None:
                        break
                    time.sleep(3.0)
            finally:
                if proc.poll() is None:
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        proc.terminate()
            time.sleep(5.0)
        log("Phase 4 (Comment replies) completed.\n")
    else:
        log("Phase 4 (Comment replies) skipped.\n")

    log("=" * 60)
    log("FULL AUTOMATION PIPELINE EXECUTION COMPLETED!")
    log("=" * 60)


if __name__ == "__main__":
    main()
