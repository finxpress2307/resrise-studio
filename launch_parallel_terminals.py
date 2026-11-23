import argparse
import os
import subprocess
import sys
import time

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable or "python"


def launch_account_terminal(
    account: str,
    task: str = "run_account",
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
    once_flag = " --once" if once else ""
    
    if task == "browsing":
        title = f"[Browsing + Feed Likes] @{account}"
        cmd_str = f"& '{PYTHON_EXE}' 'scripts\\ig_browsing.py' --account {account}"
        desc = "Feed Browsing, Likes & Vision-Aware Commenting"
    elif task == "replier":
        title = f"[Post Comments Replier] @{account}"
        cmd_str = f"& '{PYTHON_EXE}' 'scripts\\ig_replier.py' --account {account}"
        desc = "Profile Post Comments Replier & Engagement"
    else:  # run_account (Full Suite)
        title = f"[Full Automation Suite] @{account}"
        cmd_str = (
            f"& '{PYTHON_EXE}' 'run_account.py' --account {account} --mode {mode} "
            f"--feed-min {feed_min} --feed-max {feed_max} "
            f"--story-min {story_min} --story-max {story_max} "
            f"--max-reply-posts {max_reply_posts} "
            f"--sleep-min {sleep_min} --sleep-max {sleep_max}{once_flag}"
        )
        desc = f"Full Suite: Feed {feed_min}-{feed_max} | Stories {story_min}-{story_max} | Sleep {sleep_min}-{sleep_max}m"

    ps_cmd = (
        f"$Host.UI.RawUI.WindowTitle = '{title}'; "
        f"Set-Location -Path '{PROJECT_DIR}'; "
        f"Write-Host '===========================================================' -ForegroundColor Cyan; "
        f"Write-Host '  RESRISE STUDIO INSTAGRAM AUTOMATION LIVE TERMINAL' -ForegroundColor Yellow; "
        f"Write-Host '  Account: @{account}' -ForegroundColor Green; "
        f"Write-Host '  Target:  Feed {feed_min}-{feed_max} | Stories {story_min}-{story_max} | Sleep {sleep_min}-{sleep_max}m' -ForegroundColor White; "
        f"Write-Host '  Mode:    {desc}' -ForegroundColor Gray; "
        f"Write-Host '===========================================================' -ForegroundColor Cyan; "
        f"{cmd_str}"
    )

    # Use 'start powershell' to pop open a new visible terminal window
    start_cmd = f'start "{title}" powershell -NoExit -Command "{ps_cmd}"'
    subprocess.Popen(start_cmd, shell=True, cwd=PROJECT_DIR)
    print(f"✅ Launched dedicated terminal for @{account} -> {desc}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Launch separate Windows terminal windows for concurrent Instagram automation across all accounts."
    )
    parser.add_argument(
        "--task",
        choices=["run_account", "browsing", "replier"],
        default="run_account",
        help="Task to run: 'run_account' (Full suite: feed+stories+replier), 'browsing', or 'replier'",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "feed", "stories", "replier"],
        default="both",
        help="Automation mode for run_account: 'both' (default), 'feed', 'stories', or 'replier'",
    )
    parser.add_argument(
        "--accounts",
        nargs="+",
        default=["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise"],
        help=f"Accounts to launch (default: avanyamehra mairamehraofficial iamgagankumar resrise)",
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
        help="Profile posts to inspect for comments per cycle (default: 5)",
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
        help="Run only 1 complete cycle and stop",
    )
    args = parser.parse_args()

    print("=" * 65)
    print("RESRISE STUDIO — MULTI-TERMINAL INSTAGRAM AUTOMATION LAUNCHER")
    print(f"Mode:     {args.mode}")
    print(f"Feed:     {args.feed_min}-{args.feed_max} posts per cycle")
    print(f"Stories:  {args.story_min}-{args.story_max} stories per cycle")
    print(f"Sleep:    {args.sleep_min}-{args.sleep_max} minutes between cycles")
    print(f"Accounts: {', '.join('@' + a for a in args.accounts)}")
    print("=" * 65)

    for i, account in enumerate(args.accounts, 1):
        clean_acc = account.strip().lstrip("@").lower()
        if clean_acc in ACCOUNTS:
            launch_account_terminal(
                account=clean_acc,
                task=args.task,
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
            time.sleep(2.5)  # brief stagger to prevent concurrent browser initialization conflicts

    print("\n🚀 All terminals successfully launched with exact cadence:")
    print(f"Starting dedicated runner | Mode: {args.mode} | Feed: {args.feed_min}-{args.feed_max} | Stories: {args.story_min}-{args.story_max} | Sleep: {args.sleep_min}-{args.sleep_max}m")


if __name__ == "__main__":
    main()
