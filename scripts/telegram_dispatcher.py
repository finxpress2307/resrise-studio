"""
Resrise Studio - Telegram Drops Dispatcher
Automates broadcasting curated product drops and affiliate links to Telegram VIP channels.
Supports direct Telegram Bot API publishing or formatted copy-paste export.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = (
    os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
    if os.path.basename(SCRIPT_DIR).lower() == "scripts"
    else SCRIPT_DIR
)
QUEUE_FILE = os.path.join(PROJECT_DIR, "telegram_drops_queue.json")
SENT_HISTORY_FILE = os.path.join(PROJECT_DIR, "sent_telegram_drops.json")

# Channel handles mapping
CHANNEL_HANDLES = {
    "avanyamehra": "@avanyamehra_luxe",
    "mairamehraofficial": "@mairamehraclub",
    "iamgagankumar": "@gagankumar_menswear",
    "gagankumarrocks": "@gagankumar_growth",
    "resrise": "@resrise_studio",
}


def load_queue() -> list:
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {QUEUE_FILE}: {e}")
    return []


def load_sent_history() -> dict:
    if os.path.exists(SENT_HISTORY_FILE):
        try:
            with open(SENT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"sent_drop_ids": []}


def save_sent_history(history: dict):
    with open(SENT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def send_telegram_message(bot_token: str, chat_id: str, text: str, image_path: str = None) -> bool:
    """Sends a photo with caption or a text message via official Telegram Bot API."""
    try:
        if image_path and os.path.exists(image_path):
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            # Multi-part form or simple URL
            with open(image_path, "rb") as f:
                img_data = f.read()

            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            body = bytearray()

            # chat_id
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode("utf-8"))
            # caption (HTML/Markdown)
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{text}\r\n".encode("utf-8"))
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"parse_mode\"\r\n\r\nMarkdown\r\n".encode("utf-8"))
            # photo
            filename = os.path.basename(image_path)
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"{filename}\"\r\nContent-Type: image/jpeg\r\n\r\n".encode("utf-8"))
            body.extend(img_data)
            body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

            req = urllib.request.Request(url, data=bytes(body), headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            })
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("ok", False)
        else:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = json.dumps({
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("ok", False)
    except Exception as e:
        print(f"❌ Telegram API call failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Dispatch queued drops to Telegram channels.")
    parser.add_argument("--account", choices=list(CHANNEL_HANDLES.keys()) + ["all"], default="all")
    parser.add_argument("--send", action="store_true", help="Send via Telegram Bot API using TELEGRAM_BOT_TOKEN")
    parser.add_argument("--bot-token", default=os.environ.get("TELEGRAM_BOT_TOKEN", ""), help="Telegram Bot API Token")
    parser.add_argument("--force", action="store_true", help="Send even if previously marked as sent")
    args = parser.parse_args()

    queue = load_queue()
    history = load_sent_history()
    sent_ids = set(history.get("sent_drop_ids", []))

    if not queue:
        print("ℹ️ No drops found in telegram_drops_queue.json")
        return

    print("================================================================================")
    print("                    RESRISE STUDIO - TELEGRAM DROPS DISPATCHER                  ")
    print("================================================================================")

    for item in queue:
        account = item.get("account", "")
        if args.account != "all" and account != args.account:
            continue

        drop_id = item.get("id", "unknown")
        target_channel = CHANNEL_HANDLES.get(account, f"@{account}")
        drop_text = item.get("drop_text", "")
        image_path = item.get("image_path", "")
        is_sent = drop_id in sent_ids

        print(f"\n📦 Drop ID: [{drop_id}] | Account: @{account} -> Channel: {target_channel}")
        print(f"   Status: {'ALREADY SENT' if is_sent else 'PENDING BROADCAST'}")
        print(f"   Image: {image_path} (Exists: {os.path.exists(image_path)})")
        print(f"   Scheduled For: {item.get('scheduled_for', 'Immediate')}")
        print("--------------------------------------------------------------------------------")
        print(drop_text)
        print("--------------------------------------------------------------------------------")

        if args.send:
            if not args.bot_token:
                print("❌ Cannot send: TELEGRAM_BOT_TOKEN is not provided. Pass --bot-token or set in .env")
                continue
            if is_sent and not args.force:
                print("⏭️ Skipping (already sent). Pass --force to re-broadcast.")
                continue

            print(f"🚀 Broadcasting to {target_channel}...")
            success = send_telegram_message(args.bot_token, target_channel, drop_text, image_path)
            if success:
                print(f"✅ Successfully posted drop [{drop_id}] to {target_channel}!")
                sent_ids.add(drop_id)
                history["sent_drop_ids"] = list(sent_ids)
                save_sent_history(history)
            else:
                print(f"❌ Failed to post drop [{drop_id}]. Verify bot is admin of {target_channel}.")

    if not args.send:
        print("\n💡 TIP: To automatically publish to Telegram, set TELEGRAM_BOT_TOKEN in .env and run:")
        print("   python scripts/telegram_dispatcher.py --send")


if __name__ == "__main__":
    main()
