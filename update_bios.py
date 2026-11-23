import argparse
import json
import os
import sys
import time

# ALL BIOS STRICTLY UNDER THE 150-CHARACTER INSTAGRAM LIMIT
CLEAN_BIOS = {
    "avanyamehra": {
        "name": "Avanya Mehra | Editorial Model",
        "bio": (
            "📍 New Delhi · Milan · Paris\n"
            "Editorial & high-fashion muse ✨\n"
            "Represented by @resrise\n"
            "VIP Luxe Vault: @avanyamehra_luxe ⤵"
        ),
        "website": "https://t.me/avanyamehra_luxe",
        "linktree": "https://linktr.ee/avanyamehra",
        "avatar": "assets/avanya_hero.jpg",
    },
    "mairamehraofficial": {
        "name": "Maira Mehra | Saree & Style",
        "bio": (
            "🌸 Timeless drapes into everyday art\n"
            "Saree styling & travel edits ✨\n"
            "Represented by @resrise\n"
            "VIP Saree Club: @mairamehraclub ⤵"
        ),
        "website": "https://t.me/mairamehraclub",
        "linktree": "https://linktr.ee/mairamehra",
        "avatar": "assets/maira_hero.jpg",
    },
    "iamgagankumar": {
        "name": "Gagan Kumar | Menswear & Style",
        "bio": (
            "⚡ Tailored fits & minimalist style\n"
            "Curated menswear & grooming edits\n"
            "Represented by @resrise\n"
            "Men's Capsule Club: @gagankumar_menswear ⤵"
        ),
        "website": "https://t.me/gagankumar_menswear",
        "linktree": "https://linktr.ee/iamgagankumar",
        "avatar": "assets/gagan_hero.jpg",
    },
    "resrise": {
        "name": "Resrise Studio",
        "bio": (
            "✨ AI creative production & campaigns\n"
            "Curating modern muses & visual stories\n"
            "contact.resrise@gmail.com\n"
            "VIP Roster: @resrise_studio ⤵"
        ),
        "website": "https://t.me/resrise_studio",
        "linktree": "https://linktr.ee/resrisestudio",
        "avatar": "assets/avanya_amalfi.jpg",
    },
    "gagankumarrocks": {
        "name": "Gagan Kumar | Media & Systems",
        "bio": (
            "🚀 Media entrepreneur & systems architect\n"
            "Founder @resrise\n"
            "Scaling modern creator brands\n"
            "Media Systems: @gagankumar_growth ⤵"
        ),
        "website": "https://t.me/gagankumar_growth",
        "linktree": "https://linktr.ee/gagankumarrocks",
        "avatar": "assets/gagan_blazer.jpg",
    },
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = (
    os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
    if os.path.basename(SCRIPT_DIR).lower() == "scripts"
    else SCRIPT_DIR
)


def load_accounts_config() -> dict:
    """Loads accounts configuration from scripts/accounts_config.json."""
    candidates = [
        os.path.join(PROJECT_DIR, "scripts", "accounts_config.json"),
        os.path.join(SCRIPT_DIR, "accounts_config.json"),
        os.path.join(PROJECT_DIR, "accounts_config.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def get_account_link(
    account: str,
    config: dict = None,
    link_type: str = "telegram",
    custom_link: str = None,
    skip_link: bool = False,
) -> str | None:
    """Resolves profile link from accounts_config.json or CLEAN_BIOS fallback."""
    if skip_link or link_type == "none":
        return None
    if custom_link:
        return custom_link

    if config is None:
        config = load_accounts_config()

    acc_config = config.get("accounts", {}).get(account, {})
    telegram_info = acc_config.get("telegram", {})

    if link_type == "linktree":
        return (
            telegram_info.get("linktree")
            or CLEAN_BIOS.get(account, {}).get("linktree")
        )
    else:  # default "telegram"
        return telegram_info.get("url") or CLEAN_BIOS.get(account, {}).get("website")


def get_chrome_profile_dir(account: str) -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    return os.path.join(local_app_data, "Google", "Chrome", "User Data - Automation", account)


def update_profile_bio(
    account: str,
    apply_changes: bool = False,
    link_type: str = "telegram",
    custom_link: str = None,
    skip_link: bool = False,
    update_avatar: bool = False,
    config: dict = None,
) -> None:
    if account not in CLEAN_BIOS:
        print(f"No preset bio found for '{account}'.")
        return

    if config is None:
        config = load_accounts_config()

    data = CLEAN_BIOS[account]
    bio_text = data["bio"]
    bio_len = len(bio_text)
    target_link = get_account_link(
        account,
        config=config,
        link_type=link_type,
        custom_link=custom_link,
        skip_link=skip_link,
    )

    print(f"\n==========================================")
    print(f"Target Account: @{account}")
    print(f"Name: {data['name']}")
    print(f"Bio ({bio_len}/150 chars):\n{bio_text}")
    if target_link:
        print(f"Website Link ({link_type}): {target_link}")
    else:
        print("Website Link: [Skip / No link update]")
    if update_avatar and "avatar" in data:
        print(f"Avatar: {data['avatar']}")
    print(f"==========================================")

    if not apply_changes:
        print("ℹ️ Dry-run mode. Pass --apply to save this to Instagram.")
        return

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright is required for --apply mode. Run 'pip install playwright'.")
        return

    user_data_dir = get_chrome_profile_dir(account)
    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lock_path = os.path.join(user_data_dir, lock_file)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    with sync_playwright() as p:
        print(f"Launching Chrome for @{account}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            viewport={"width": 1100, "height": 800},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to https://www.instagram.com/accounts/edit/ ...")
        page.goto("https://www.instagram.com/accounts/edit/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4.0)

        # 1. Update Profile Photo if requested
        if update_avatar and "avatar" in data:
            avatar_rel = data["avatar"]
            avatar_full = os.path.normpath(os.path.join(PROJECT_DIR, avatar_rel))
            if os.path.exists(avatar_full):
                try:
                    file_input = page.locator("input[type='file'][accept*='image']").first
                    if file_input.count() > 0:
                        print(f"Uploading new profile photo from {avatar_rel}...")
                        file_input.set_input_files(avatar_full)
                        time.sleep(3.5)
                        print("✅ Profile photo uploaded!")
                    else:
                        change_btn = page.locator("button:has-text('Change profile photo'), span:has-text('Change photo')").first
                        if change_btn.is_visible(timeout=2000):
                            with page.expect_file_chooser() as fc_info:
                                change_btn.click(force=True)
                            file_chooser = fc_info.value
                            file_chooser.set_files(avatar_full)
                            time.sleep(3.5)
                            print("✅ Profile photo selected via file chooser!")
                except Exception as e:
                    print(f"Notice during avatar upload: {e}")

        # 2. Update Bio
        bio_box = page.locator("textarea#pepBio, textarea[name='biography'], textarea").first
        if bio_box.is_visible(timeout=5000):
            print(f"Updating Bio ({bio_len} chars)...")
            bio_box.click(force=True)
            time.sleep(0.5)
            page.keyboard.press("Control+A")
            time.sleep(0.2)
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            bio_box.fill(bio_text)
            time.sleep(1.0)
        else:
            print("⚠️ Bio input box not visible. Please check login state.")

        # 3. Update Website / Profile Link
        if target_link:
            website_box = page.locator(
                "input#pepWebsite, input[name='website'], input[placeholder*='Website' i], input[aria-label*='Website' i]"
            ).first
            if website_box.is_visible(timeout=3000):
                try:
                    if website_box.is_disabled(timeout=2000):
                        print("ℹ️ Note: Instagram has marked the Website input as disabled on desktop web ('Editing links is only available on mobile'). Skipping website input.")
                    else:
                        print(f"Updating Website Link -> {target_link} ...")
                        website_box.click(force=True, timeout=2000)
                        time.sleep(0.3)
                        page.keyboard.press("Control+A")
                        time.sleep(0.2)
                        page.keyboard.press("Backspace")
                        time.sleep(0.2)
                        website_box.fill(target_link, timeout=3000)
                        time.sleep(0.5)
                except Exception as e:
                    print(f"ℹ️ Website field not editable on desktop web: {e}")
            else:
                print("ℹ️ Note: Website input field not found on edit page.")

        # 4. Submit Changes
        submit_btn = page.locator("div[role='button']:text-is('Submit'), button:text-is('Submit')").first
        if submit_btn.is_visible(timeout=3000):
            submit_btn.click(force=True)
            print("✅ Clicked Submit! Profile updated successfully.")
            time.sleep(4.0)
        else:
            print("⚠️ Submit button not found. Please click Submit manually in the browser.")
            time.sleep(5.0)

        context.close()


def main():
    parser = argparse.ArgumentParser(
        description="Clean and update Instagram bios strictly under the 150-char limit and set profile links."
    )
    parser.add_argument(
        "--account",
        choices=list(CLEAN_BIOS.keys()) + ["all"],
        default="all",
        help="Target account to update (or 'all')",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply updates directly to Instagram via Chrome automation",
    )
    parser.add_argument(
        "--link-type",
        choices=["telegram", "linktree", "none"],
        default="telegram",
        help="Type of link to set from accounts_config.json (default: telegram)",
    )
    parser.add_argument(
        "--use-linktree",
        action="store_true",
        help="Convenience flag: use Linktree URL instead of Telegram URL",
    )
    parser.add_argument(
        "--custom-link",
        type=str,
        default=None,
        help="Custom URL to set instead of accounts_config.json link",
    )
    parser.add_argument(
        "--skip-link",
        action="store_true",
        help="Skip updating website link (only update bio text)",
    )
    parser.add_argument(
        "--update-avatar",
        action="store_true",
        help="Upload new profile picture from assets/ directory",
    )
    args = parser.parse_args()

    link_type = "linktree" if args.use_linktree else args.link_type
    config = load_accounts_config()

    targets = list(CLEAN_BIOS.keys()) if args.account == "all" else [args.account]
    for acc in targets:
        update_profile_bio(
            acc,
            apply_changes=args.apply,
            link_type=link_type,
            custom_link=args.custom_link,
            skip_link=args.skip_link,
            update_avatar=args.update_avatar,
            config=config,
        )


if __name__ == "__main__":
    main()
