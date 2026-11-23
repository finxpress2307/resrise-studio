import argparse
import os
import subprocess

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]


def parse_account(value: str) -> str:
    cleaned = value.strip().lstrip("@").lower()
    if cleaned not in ACCOUNTS:
        raise argparse.ArgumentTypeError(
            f"Unsupported account '{value}'. Choose from: {', '.join(ACCOUNTS)}"
        )
    return cleaned


def get_chrome_profile_dir(account: str) -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    return os.path.join(local_app_data, "Google", "Chrome", "User Data - Automation", account)


def open_login_browser(account: str) -> None:
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = os.path.join(local_app_data, r"Google\Chrome\Application\chrome.exe")

    user_data_dir = get_chrome_profile_dir(account)
    os.makedirs(user_data_dir, exist_ok=True)

    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lock_path = os.path.join(user_data_dir, lock_file)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    print("=" * 60)
    print(f"OPENING CHROME FOR INSTAGRAM LOGIN (@{account})")
    print("=" * 60)
    print(f"Profile: {user_data_dir}\n")
    print("1. A Google Chrome window will open to Instagram.")
    print(f"2. Log into @{account} as you normally would.")
    print("3. Once you see your feed, CLOSE that Chrome window completely.")
    print(f"4. Your session is saved for automation on @{account}.")
    print("=" * 60)

    cmd = [
        chrome_path,
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.instagram.com/",
    ]

    subprocess.Popen(cmd)
    print(f"\nChrome launched for @{account}! Look for the new Chrome window on your screen or taskbar.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Open Chrome to log into an Instagram automation profile.")
    parser.add_argument(
        "-a",
        "--account",
        required=True,
        type=parse_account,
        help=f"Instagram handle to log into ({', '.join(ACCOUNTS)})",
    )
    args = parser.parse_args()
    open_login_browser(args.account)
