"""
Instagram Graph API v27.0 Carousel Publisher & Due-Time Dispatcher
===================================================================
Production-grade, zero-Playwright automated publisher designed for Windows Task Scheduler.

Key Safeguards:
1. API Version: Enforces Graph API v27.0.
2. Format: Converts all images to strict JPEG format.
3. Hosting & Cleanup: Uploads temporary slides to Cloudinary HTTPS, destroys them after publish to keep storage free.
4. Double-Post Prevention: Locks posts as 'PUBLISHING' before starting any upload.
5. Error 9007 Prevention: Polls container status until 'FINISHED' before calling /media_publish.
6. Idempotent: Checks swarm_queue.json for APPROVED posts where now >= scheduled_for.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO

import httpx
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v27.0")
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
QUEUE_PATH = os.path.join(PROJECT_DIR, "swarm_queue.json")

# Cloudinary credentials
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Check Cloudinary availability
HAS_CLOUDINARY = False
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    try:
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True,
        )
        HAS_CLOUDINARY = True
    except ImportError:
        pass


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [IG-API-PUBLISHER] {msg}", flush=True)


def load_queue() -> list:
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_queue(q: list) -> None:
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(q, f, indent=2, ensure_ascii=False)


def get_account_credentials(account: str) -> tuple[str, str]:
    """Retrieve the Instagram Business Account ID and Access Token for an account."""
    clean_acc = account.upper().replace("@", "")
    ig_id = os.getenv(f"IG_ID_{clean_acc}")
    token = os.getenv(f"IG_TOKEN_{clean_acc}")
    return ig_id or "", token or ""


def ensure_jpeg(image_path: str) -> tuple[bytes, str]:
    """Verify and convert image to strict JPEG bytes if needed."""
    with Image.open(image_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        out_buf = BytesIO()
        img.save(out_buf, format="JPEG", quality=95)
        return out_buf.getvalue(), "image/jpeg"


def upload_slide_to_cloud(image_path: str, post_id: str, slide_idx: int) -> tuple[str, str]:
    """Uploads a JPEG slide to Cloudinary, returning (public_https_url, public_id)."""
    if not HAS_CLOUDINARY:
        raise RuntimeError("Cloudinary is not configured. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET in .env.")

    jpeg_bytes, _ = ensure_jpeg(image_path)
    public_id = f"resrise_posts/{post_id}_slide_{slide_idx}_{int(time.time())}"

    res = cloudinary.uploader.upload(
        jpeg_bytes,
        public_id=public_id,
        folder="resrise_posts",
        resource_type="image",
        format="jpg",
    )
    return res["secure_url"], res["public_id"]


def cleanup_cloud_assets(public_ids: list[str]) -> None:
    """Deletes temporary images from Cloudinary after successful Instagram publication."""
    if not HAS_CLOUDINARY:
        return
    for pid in public_ids:
        try:
            cloudinary.uploader.destroy(pid)
            log(f"🧹 Cleaned up temporary cloud asset: {pid}")
        except Exception as e:
            log(f"⚠️ Warning: Failed to clean cloud asset {pid}: {e}")


def poll_container_status(client: httpx.Client, container_id: str, access_token: str, max_wait: int = 60) -> bool:
    """
    Polls container status every 3s until FINISHED.
    Prevents Error 9007 ('Media ID is not available').
    """
    poll_url = f"{GRAPH_BASE_URL}/{container_id}"
    start_time = time.time()

    while time.time() - start_time < max_wait:
        resp = client.get(
            poll_url,
            params={"fields": "status_code", "access_token": access_token},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("status_code")
            if code == "FINISHED":
                return True
            if code == "ERROR":
                raise RuntimeError(f"Instagram media container processing failed: {data}")
            if code in ("IN_PROGRESS", "EXPIRED"):
                log(f"Container {container_id} status: {code}. Waiting 3s...")
        time.sleep(3.0)

    raise TimeoutError(f"Container {container_id} timed out waiting for FINISHED status after {max_wait}s.")


def publish_carousel_api(item: dict) -> dict:
    """
    Publishes a 3-slide carousel via official Meta Graph API v27.0.
    """
    account = item.get("account", "").lower()
    post_id = item.get("id", "post")
    ig_user_id, access_token = get_account_credentials(account)

    if not ig_user_id or not access_token:
        raise ValueError(f"Missing IG credentials for account @{account}. Set IG_ID_{account.upper()} and IG_TOKEN_{account.upper()} in .env.")

    media_files = item.get("media_files", [])
    if not media_files:
        raise ValueError(f"No media_files found for post {post_id}.")

    # Absolute file paths
    abs_paths = [os.path.join(PROJECT_DIR, f) if not os.path.isabs(f) else f for f in media_files]
    for p in abs_paths:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Media file not found: {p}")

    public_ids_to_clean = []
    item_container_ids = []

    with httpx.Client(timeout=30.0) as client:
        try:
            # 1. Upload slides to public HTTPS & create carousel item containers
            log(f"Uploading {len(abs_paths)} slide(s) to temporary cloud storage for [id:{post_id}]...")
            for idx, p in enumerate(abs_paths, 1):
                cloud_url, pub_id = upload_slide_to_cloud(p, post_id, idx)
                public_ids_to_clean.append(pub_id)

                # Create item container
                log(f"Creating item container {idx}/{len(abs_paths)} for @{account}...")
                item_payload = {
                    "image_url": cloud_url,
                    "is_carousel_item": "true",
                    "access_token": access_token,
                }
                res = client.post(f"{GRAPH_BASE_URL}/{ig_user_id}/media", data=item_payload)
                if res.status_code != 200:
                    raise RuntimeError(f"Failed to create carousel item container {idx}: {res.text}")
                item_cid = res.json().get("id")
                item_container_ids.append(item_cid)
                time.sleep(1.0)

            # 2. Create Carousel parent container
            caption = item.get("caption", "").strip()
            log(f"Creating parent carousel container for [id:{post_id}]...")
            carousel_payload = {
                "media_type": "CAROUSEL",
                "children": ",".join(item_container_ids),
                "caption": caption,
                "access_token": access_token,
            }
            res = client.post(f"{GRAPH_BASE_URL}/{ig_user_id}/media", data=carousel_payload)
            if res.status_code != 200:
                raise RuntimeError(f"Failed to create parent carousel container: {res.text}")
            carousel_cid = res.json().get("id")

            # 3. Safeguard: Poll status until FINISHED (Error 9007 Prevention)
            log(f"Polling carousel container {carousel_cid} status...")
            poll_container_status(client, carousel_cid, access_token, max_wait=60)
            log(f"✅ Container {carousel_cid} is ready for publishing!")

            # 4. Publish carousel
            log(f"Publishing container {carousel_cid} to Instagram...")
            publish_payload = {
                "creation_id": carousel_cid,
                "access_token": access_token,
            }
            res = client.post(f"{GRAPH_BASE_URL}/{ig_user_id}/media_publish", data=publish_payload)
            if res.status_code != 200:
                raise RuntimeError(f"Failed to publish carousel container: {res.text}")

            published_ig_id = res.json().get("id")
            log(f"🎉 Successfully published [id:{post_id}] to @{account}! IG Media ID: {published_ig_id}")

            # 5. Clean up temporary cloud assets
            cleanup_cloud_assets(public_ids_to_clean)

            return {"success": True, "ig_media_id": published_ig_id}

        except Exception as e:
            cleanup_cloud_assets(public_ids_to_clean)
            raise e


def dispatch_due_posts(force: bool = False, target_account: str = None) -> None:
    """
    Scans swarm_queue.json for APPROVED posts whose scheduled_for time has passed.
    Uses 'PUBLISHING' state to prevent duplicate publishing on overlapping runs.
    """
    queue = load_queue()
    now = datetime.now()
    log(f"Scanning swarm queue (Current Time: {now.strftime('%Y-%m-%d %I:%M %p')})...")

    due_items = []
    for item in queue:
        if item.get("status") != "APPROVED":
            continue
        if target_account and item.get("account", "").lower() != target_account.lower():
            continue

        sched_str = item.get("scheduled_for")
        if not sched_str and not force:
            continue

        is_due = force
        if sched_str and not force:
            try:
                target_dt = datetime.strptime(sched_str, "%Y-%m-%d %I:%M %p")
                if now >= target_dt:
                    is_due = True
            except Exception:
                pass

        if is_due:
            due_items.append(item)

    if not due_items:
        log("No posts are currently due for publishing.")
        return

    log(f"Found {len(due_items)} post(s) ready to publish.")

    for item in due_items:
        item_id = item.get("id")
        account = item.get("account")

        # Double-post safeguard: Lock status as 'PUBLISHING' and save immediately
        item["status"] = "PUBLISHING"
        save_queue(queue)
        log(f"🔒 Locked [id:{item_id}] as 'PUBLISHING'. Starting API workflow...")

        try:
            result = publish_carousel_api(item)
            item["status"] = "PUBLISHED"
            item["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item["ig_media_id"] = result.get("ig_media_id")
            save_queue(queue)
            log(f"✅ [id:{item_id}] successfully marked as PUBLISHED.")
        except Exception as err:
            log(f"❌ Failed to publish [id:{item_id}]: {err}")
            item["status"] = "FAILED_PUBLISH"
            item["publish_error"] = str(err)
            save_queue(queue)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram Graph API v27.0 Publisher & Dispatcher")
    parser.add_argument("--force", action="store_true", help="Force publish all APPROVED posts regardless of scheduled_for time")
    parser.add_argument("-a", "--account", help="Only process posts for a specific account")
    args = parser.parse_args()

    dispatch_due_posts(force=args.force, target_account=args.account)
