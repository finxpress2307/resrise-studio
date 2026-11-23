"""Script to cancel and delete all natively scheduled posts on Instagram."""
import os
import sys
import time
from playwright.sync_api import sync_playwright

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]


def get_chrome_profile_dir(account: str) -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    return os.path.join(local_app_data, "Google", "Chrome", "User Data - Automation", account)


def cancel_scheduled_posts_for_account(account: str, dry_run: bool = False) -> None:
    user_data_dir = get_chrome_profile_dir(account)
    if not os.path.exists(user_data_dir):
        print(f"Profile directory for @{account} does not exist. Skipping.")
        return

    # Clean locks
    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lock_path = os.path.join(user_data_dir, lock_file)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    print(f"\n=======================================================")
    print(f"Checking scheduled posts for @{account}...")
    print(f"=======================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            viewport={"width": 1200, "height": 820},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto("https://www.instagram.com/scheduled_content/", wait_until="domcontentloaded", timeout=45000)
            time.sleep(4.0)

            # Check if there are scheduled posts
            items = page.locator("article, div[role='dialog'] div[role='button']:has(img), a:has(img)").all()
            print(f"Found scheduled content container. Scanning for scheduled items...")

            # Look for 3-dots option buttons or scheduled rows
            deleted_count = 0
            while True:
                # Find options button on scheduled post
                dots_btn = page.locator("svg[aria-label='Options'], svg[aria-label='More options'], div[role='button']:has(svg[aria-label='Options'])").first
                if not dots_btn.is_visible(timeout=3000):
                    break

                if dry_run:
                    print(f"[Dry-run] Would delete scheduled post on @{account}")
                    break

                dots_btn.click(force=True)
                time.sleep(1.0)

                delete_btn = page.locator("button:has-text('Delete'), div[role='button']:has-text('Delete'), button:has-text('Cancel post')").first
                if delete_btn.is_visible(timeout=3000):
                    delete_btn.click(force=True)
                    time.sleep(1.0)

                    # Confirm delete in dialog
                    confirm_btn = page.locator("button:has-text('Delete'), div[role='dialog'] button:has-text('Delete')").first
                    if confirm_btn.is_visible(timeout=3000):
                        confirm_btn.click(force=True)
                        deleted_count += 1
                        print(f"✅ Deleted scheduled post #{deleted_count} on @{account}")
                        time.sleep(3.0)
                else:
                    # Close dialog
                    page.keyboard.press("Escape")
                    time.sleep(1.0)
                    break

            print(f"Done for @{account}. Total cancelled/deleted posts: {deleted_count}")

        except Exception as e:
            print(f"Notice while checking @{account}: {e}")
        finally:
            context.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cancel and stop all scheduled posts on Instagram natively.")
    parser.add_argument("--account", choices=ACCOUNTS + ["all"], default="all")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    args = parser.parse_args()

    targets = ACCOUNTS if args.account == "all" else [args.account]
    for acc in targets:
        cancel_scheduled_posts_for_account(acc, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
