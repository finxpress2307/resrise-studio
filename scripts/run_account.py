import argparse
import os
import random
import subprocess
import sys
import time
from datetime import datetime

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "scripts") if os.path.isdir(os.path.join(SCRIPT_DIR, "scripts")) else SCRIPT_DIR
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR).lower() == "scripts" else SCRIPT_DIR

from ig_network_engager import run_following_engager
from ig_replier import simulate_comment_replies, is_already_responded
from run_daily_automation import run_story_automation


def parse_account(value: str) -> str:
    cleaned = value.strip().lstrip("@").lower()
    if cleaned not in ACCOUNTS:
        raise argparse.ArgumentTypeError(
            f"Unsupported account '{value}'. Choose from: {', '.join(ACCOUNTS)}"
        )
    return cleaned


def log(account: str, msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [@{account}] [RUNNER] {msg}", flush=True)


def run_cycle_for_account(
    account: str,
    mode: str = "both",
    feed_min: int = 10,
    feed_max: int = 12,
    story_min: int = 10,
    story_max: int = 12,
    max_reply_posts: int = 5,
) -> None:
    """Executes one cohesive automation cycle for a single account with 10-12 feed & story targets."""
    # Pick randomized targets within 10-12 range
    feed_target = random.randint(min(feed_min, feed_max), max(feed_min, feed_max))
    story_target = random.randint(min(story_min, story_max), max(story_min, story_max))

    log(account, f"--- Beginning automation cycle (Feed target: {feed_target} | Stories target: {story_target}) ---")

    # 1. Main Feed Browsing & Following-Priority Engagement (Target: 10-12 posts)
    if mode in ("both", "feed"):
        log(account, f"Step 1/3: Following-priority network engagement (Target: {feed_target} posts, likes & contextual comments)...")
        try:
            run_following_engager(
                account,
                max_comments=feed_target,
                max_feed_scrolls=25,
                draft_only=False,
                headless=False,
            )
        except Exception as e:
            log(account, f"Following engagement note: {e}")
        time.sleep(random.uniform(6.0, 12.0))

    # 2. Stories Watching & Reacting (Top Tray: 10-12 stories)
    if mode in ("both", "stories"):
        log(account, f"Step 2/3: Watching & reacting to top-tray stories (Target: {story_target} stories)...")
        try:
            run_story_automation(account, max_stories=story_target)
        except Exception as e:
            log(account, f"Story interaction note: {e}")
        time.sleep(random.uniform(6.0, 12.0))

    # 3. Post Comments Auto-Responding (Profile posts for unreplied comments)
    if mode in ("both", "replier"):
        log(account, f"Step 3/3: Checking latest {max_reply_posts} profile posts for unreplied comments & bio club routing...")
        try:
            simulate_comment_replies(
                account,
                max_posts=max_reply_posts,
                max_replies_per_post=5,
            )
        except Exception as e:
            log(account, f"Comment reply note: {e}")

    log(account, "--- Cycle complete ---")


def main_loop(
    account: str,
    mode: str = "both",
    feed_min: int = 10,
    feed_max: int = 12,
    story_min: int = 10,
    story_max: int = 12,
    max_reply_posts: int = 5,
    sleep_min: int = 15,
    sleep_max: int = 20,
    once: bool = False,
) -> None:
    # Set Windows console window title
    if os.name == "nt":
        os.system(f"title [Instagram Automation] @{account}")

    cycle = 1
    log(
        account,
        f"Starting dedicated runner | Mode: {mode} | Feed: {feed_min}-{feed_max} | Stories: {story_min}-{story_max} | Sleep: {sleep_min}-{sleep_max}m",
    )

    try:
        while True:
            log(account, f"========== Cycle #{cycle} ==========")
            run_cycle_for_account(
                account,
                mode=mode,
                feed_min=feed_min,
                feed_max=feed_max,
                story_min=story_min,
                story_max=story_max,
                max_reply_posts=max_reply_posts,
            )

            if once:
                log(account, "Finished single cycle (--once specified). Exiting.")
                break

            # Sleep 15-20 minutes with random jitter
            rest_minutes = random.randint(min(sleep_min, sleep_max), max(sleep_min, sleep_max))
            rest_seconds = rest_minutes * 60 + random.randint(5, 45)
            log(account, f"Resting for {rest_minutes} minutes ({rest_seconds}s) before Cycle #{cycle + 1}...")
            time.sleep(rest_seconds)
            cycle += 1

    except KeyboardInterrupt:
        log(account, "Runner stopped by user (Ctrl+C).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dedicated Instagram Automation Runner for a single account (Feed: 10-12 | Stories: 10-12 | Sleep: 15-20m)."
    )
    parser.add_argument(
        "-a",
        "--account",
        required=True,
        type=parse_account,
        help=f"Instagram account handle to run ({', '.join(ACCOUNTS)})",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "feed", "stories", "replier"],
        default="both",
        help="What to run: 'both' (feed + stories + replier), 'feed', 'stories', or 'replier'",
    )
    parser.add_argument(
        "--feed-min",
        type=int,
        default=10,
        help="Minimum feed posts per cycle (default: 10)",
    )
    parser.add_argument(
        "--feed-max",
        type=int,
        default=12,
        help="Maximum feed posts per cycle (default: 12)",
    )
    parser.add_argument(
        "--story-min",
        type=int,
        default=10,
        help="Minimum stories to watch per cycle (default: 10)",
    )
    parser.add_argument(
        "--story-max",
        type=int,
        default=12,
        help="Maximum stories to watch per cycle (default: 12)",
    )
    parser.add_argument(
        "--max-reply-posts",
        type=int,
        default=5,
        help="Number of profile posts to inspect for comments (default: 5)",
    )
    parser.add_argument(
        "--sleep-min",
        type=int,
        default=15,
        help="Minimum resting time in minutes between cycles (default: 15)",
    )
    parser.add_argument(
        "--sleep-max",
        type=int,
        default=20,
        help="Maximum resting time in minutes between cycles (default: 20)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run only 1 cycle and then exit",
    )
    args = parser.parse_args()

    main_loop(
        account=args.account,
        mode=args.mode,
        feed_min=args.feed_min,
        feed_max=args.feed_max,
        story_min=args.story_min,
        story_max=args.story_max,
        max_reply_posts=args.max_reply_posts,
        sleep_min=args.sleep_min,
        sleep_max=args.sleep_max,
        once=args.once,
    )
