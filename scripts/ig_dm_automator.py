"""
Resrise Studio - Instagram DM Automator
Scans recent post comments for product purchase intent (e.g. 'link', 'where to buy', 'saree', 'price')
and automatically delivers the verified product link directly to their Instagram DMs.
Includes safety rate limiters (max 10-15 DMs per run) and deduplication history.
"""

import argparse
import json
import os
import sys
import time
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = (
    os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
    if os.path.basename(SCRIPT_DIR).lower() == "scripts"
    else SCRIPT_DIR
)
DM_HISTORY_FILE = os.path.join(PROJECT_DIR, "dm_sent_history.json")
ACCOUNTS_CONFIG = os.path.join(SCRIPT_DIR, "accounts_config.json")
AFFILIATE_CONFIG = os.path.join(PROJECT_DIR, "affiliate_config.json")

# Keywords that trigger a product link DM
BUY_INTENT_TRIGGERS = [
    r"\blink\b",
    r"\blinks\b",
    r"\bwhere to buy\b",
    r"\bwhere did you get\b",
    r"\bdetails\b",
    r"\bprice\b",
    r"\bcost\b",
    r"\bsaree\b",
    r"\bdress\b",
    r"\bgown\b",
    r"\boutfit\b",
    r"\bshirt\b",
    r"\bjacket\b",
    r"\bchoker\b",
    r"\bjewelry\b",
    r"\bperfume\b",
]

# Product Link Templates per Persona
PERSONA_PRODUCT_DMS = {
    "avanyamehra": (
        "Hey! ✨ Here is the verified shopping source for this Parisian look:\n\n"
        "👉 Draped Cowl Maxi Dress & Jewelry: https://www.amazon.in/s?k=women+draped+cowl+neck+sleeveless+bodycon+maxi+dress+brown&tag=gaganresrise-21\n"
        "👉 More high-street dupes in our VIP Vault: https://t.me/avanyamehra_luxe\n\n"
        "Hope you love the fit! 🤍 (#affiliate)"
    ),
    "mairamehraofficial": (
        "Namaste! 🌸 So glad you loved this saree drape!\n\n"
        "Here are the exact acquisition links:\n"
        "👉 Metallic Tissue Silk Saree: https://www.amazon.in/s?k=metallic+tissue+silk+saree+gold+scalloped+border&tag=gaganresrise-21\n"
        "👉 Antique Kundan Pearl Choker: https://www.amazon.in/s?k=zaveri+pearls+multi+strand+kundan+choker+set&tag=gaganresrise-21\n"
        "👉 Join our VIP Club for more royal edits: https://t.me/mairamehraclub\n\n"
        "Stay graceful! ✨ (#affiliate)"
    ),
    "iamgagankumar": (
        "Hey man! ⚡ Appreciate the comment on the fit.\n\n"
        "Here are the direct pieces from this capsule:\n"
        "👉 Black Velvet Bandhgala: https://www.amazon.in/s?k=men+black+velvet+bandhgala+suit+jacket+wedding&tag=gaganresrise-21\n"
        "👉 Signature Scent (Bella Vita Luxury EDP): https://www.amazon.in/dp/B0DBZTZP67?tag=gaganresrise-21\n"
        "👉 Curated Menswear Community: https://t.me/gagankumar_menswear\n\n"
        "Stay sharp! ⚡ (#affiliate)"
    ),
    "resrise": (
        "Hello from Resrise Studio! ✨\n\n"
        "Here are the lighting & studio production specs from this campaign:\n"
        "👉 100W Continuous Studio COB Lighting: https://www.amazon.in/s?k=cob+continuous+video+light+100w+bowens+mount+softbox&tag=gaganresrise-21\n"
        "👉 Brand collaborations & talent licensing: https://t.me/resrise_studio\n\n"
        "Best regards, Resrise Team ✨"
    ),
    "gagankumarrocks": (
        "Hey! 🚀 Here is the founder workstation setup from today's post:\n\n"
        "👉 Cardioid Dynamic Podcast Mic: https://www.amazon.in/s?k=dynamic+studio+podcast+microphone+usb+xlr+cardioid&tag=gaganresrise-21\n"
        "👉 Wireless Mechanical Keyboard: https://www.amazon.in/s?k=wireless+mechanical+keyboard+75+percent+hot+swappable&tag=gaganresrise-21\n"
        "👉 Full AI media systems blueprint: https://t.me/gagankumar_growth\n\n"
        "Keep building! 🚀"
    ),
}


def load_dm_history() -> dict:
    if os.path.exists(DM_HISTORY_FILE):
        try:
            with open(DM_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"messaged_users": {}}


def save_dm_history(history: dict):
    with open(DM_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def get_chrome_profile_dir(account: str) -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    return os.path.join(local_app_data, "Google", "Chrome", "User Data - Automation", account)


def has_buy_intent(comment_text: str) -> bool:
    comment_lower = comment_text.lower()
    for pattern in BUY_INTENT_TRIGGERS:
        if re.search(pattern, comment_lower):
            return True
    return False


def run_dm_automation(account: str, max_dms: int = 5, dry_run: bool = False):
    print(f"\n=======================================================")
    print(f"       RESRISE STUDIO - INSTAGRAM DM AUTOMATION        ")
    print(f"       Account: @{account} | Max DMs: {max_dms}        ")
    print(f"=======================================================")

    dm_template = PERSONA_PRODUCT_DMS.get(account)
    if not dm_template:
        print(f"❌ No product DM template defined for @{account}")
        return

    history = load_dm_history()
    account_history = history.setdefault("messaged_users", {}).setdefault(account, [])

    if dry_run:
        print("ℹ️ Running in DRY-RUN mode. No real DMs will be sent.")
        print("Template Preview:\n-------------------------------------------------------")
        print(dm_template)
        print("-------------------------------------------------------")
        return

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright is not installed. Run 'pip install playwright'.")
        return

    user_data_dir = get_chrome_profile_dir(account)
    if not os.path.exists(user_data_dir):
        print(f"❌ Chrome profile for @{account} not found at {user_data_dir}")
        return

    # Clean stale locks
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lp = os.path.join(user_data_dir, lock)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    dms_sent = 0

    with sync_playwright() as p:
        print(f"Launching persistent Chrome for @{account}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            viewport={"width": 1100, "height": 800},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Instagram profile to find latest post...")
        page.goto(f"https://www.instagram.com/{account}/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4.0)

        # Find first post link
        first_post = page.locator("article a[href*='/p/']").first
        if not first_post.is_visible(timeout=5000):
            print("⚠️ No post found on profile feed.")
            context.close()
            return

        first_post.click()
        time.sleep(3.5)

        # Scan comments
        print("Scanning post comments for buy intent triggers...")
        comment_rows = page.locator("ul ul li").all()
        print(f"Found {len(comment_rows)} comment elements.")

        users_to_message = []
        for row in comment_rows:
            try:
                text = row.inner_text()
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                if not lines:
                    continue
                author = lines[0]
                content = " ".join(lines[1:])

                if author.lower() in [account.lower(), "instagram"]:
                    continue
                if author in account_history:
                    continue

                if has_buy_intent(content):
                    print(f"🎯 Buy intent detected from @{author}: '{content[:60]}...'")
                    users_to_message.append(author)
                    if len(users_to_message) >= max_dms:
                        break
            except Exception:
                continue

        if not users_to_message:
            print("ℹ️ No new unanswered buy-intent comments found on the latest post.")
        else:
            print(f"Found {len(users_to_message)} users requesting links. Sending DMs...")

        for target_user in users_to_message:
            try:
                print(f"Opening direct chat with @{target_user}...")
                page.goto(f"https://www.instagram.com/direct/new/", wait_until="domcontentloaded", timeout=45000)
                time.sleep(3.0)

                # Search username
                search_box = page.locator("input[name='queryBox'], input[placeholder*='Search']").first
                if search_box.is_visible(timeout=5000):
                    search_box.fill(target_user)
                    time.sleep(2.5)

                    # Click first user result
                    user_select = page.locator(f"span:has-text('{target_user}')").first
                    if user_select.is_visible(timeout=4000):
                        user_select.click()
                        time.sleep(1.0)

                        chat_btn = page.locator("div[role='button']:has-text('Chat')").first
                        if chat_btn.is_visible(timeout=3000):
                            chat_btn.click()
                            time.sleep(3.0)

                            # Send DM
                            msg_box = page.locator("div[role='textbox'][aria-label*='Message']").first
                            if msg_box.is_visible(timeout=4000):
                                msg_box.click()
                                time.sleep(0.5)
                                msg_box.fill(dm_template)
                                time.sleep(1.0)
                                page.keyboard.press("Enter")
                                time.sleep(2.0)
                                print(f"✅ Successfully sent product link DM to @{target_user}!")

                                account_history.append(target_user)
                                dms_sent += 1
                                save_dm_history(history)
                                time.sleep(15.0)  # Safety cooldown between DMs
            except Exception as e:
                print(f"Notice sending DM to @{target_user}: {e}")

        print(f"\nCompleted run for @{account}. Total DMs sent: {dms_sent}")
        context.close()


def main():
    parser = argparse.ArgumentParser(description="Instagram Product Link DM Automator.")
    parser.add_argument("--account", choices=list(PERSONA_PRODUCT_DMS.keys()) + ["all"], default="all")
    parser.add_argument("--max-dms", type=int, default=5, help="Maximum DMs to send per account (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Preview templates without sending DMs")
    args = parser.parse_args()

    accounts = list(PERSONA_PRODUCT_DMS.keys()) if args.account == "all" else [args.account]
    for acc in accounts:
        run_dm_automation(acc, max_dms=args.max_dms, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
