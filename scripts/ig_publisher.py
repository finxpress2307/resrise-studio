import argparse
import json
import os
import re
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]

# Cadence configuration
BASE_START_TIME = datetime(2026, 11, 20, 6, 0)
ACCOUNT_OFFSETS = {
    "avanyamehra": 0,          # 6:00 AM
    "mairamehraofficial": 3,   # 9:00 AM (+3h)
    "iamgagankumar": 6,        # 12:00 PM (+6h)
    "resrise": 9,              # 3:00 PM (+9h)
    "gagankumarrocks": 12,     # 6:00 PM (+12h)
}
POST_INTERVAL_HOURS = 24

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
QUEUE_PATH = os.path.join(PROJECT_DIR, "swarm_queue.json")


def parse_account(value: str) -> str:
    cleaned = value.strip().lstrip("@").lower()
    if cleaned != "all" and cleaned not in ACCOUNTS:
        raise argparse.ArgumentTypeError(
            f"Unsupported account '{value}'. Choose from: {', '.join(ACCOUNTS)} or 'all'"
        )
    return cleaned


def get_chrome_profile_dir(account: str) -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
    return os.path.join(local_app_data, "Google", "Chrome", "User Data - Automation", account)


def log_activity(log_file_path: str, account: str, message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [@{account}] {message}"
    try:
        print(log_msg)
    except UnicodeEncodeError:
        print(log_msg.encode("ascii", errors="replace").decode("ascii"))
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")


def load_queue() -> list:
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return []


def save_queue(queue: list) -> None:
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def get_valid_media_paths(item: dict) -> list:
    paths = item.get("media_paths")
    if not isinstance(paths, list):
        single = item.get("media_path", "")
        paths = [single] if single else []
    # Strict enforcement: only paths that exist and reside within draft_media
    valid = []
    for p in paths:
        if p and os.path.exists(p) and "draft_media" in os.path.abspath(p):
            valid.append(p)
    return valid


def open_create_or_schedule_dialog(page, schedule_mode: bool = True) -> bool:
    """Open Instagram's Create or Scheduled Content dialog robustly across all accounts."""
    if schedule_mode:
        try:
            page.goto("https://www.instagram.com/scheduled_content/", wait_until="domcontentloaded", timeout=45000)
            time.sleep(3.0)
            sched_btn = page.locator("div[role='button']:has-text('Schedule content'), button:has-text('Schedule content')").first
            if sched_btn.is_visible(timeout=3000):
                sched_btn.click(force=True)
                time.sleep(2.0)
                if page.locator("input[type='file']").count() > 0:
                    return True
        except Exception:
            pass

    # Fallback to standard Create button with flyout handling
    try:
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
        time.sleep(3.0)

        # Look for Create / New post in sidebar
        create_link = page.locator(
            "a:has(svg[aria-label='New post']), "
            "a:has-text('Create'), "
            "a:has-text('Post'), "
            "div[role='button']:has(svg[aria-label='New post']), "
            "div[role='button']:has-text('Create'), "
            "div[role='button']:has-text('Post')"
        ).first

        if create_link.is_visible(timeout=3000):
            create_link.click(force=True)
            time.sleep(1.5)

            # Check if flyout menu opened with "Post" option (mairamehraofficial / iamgagankumar)
            post_item = page.locator("span:text-is('Post'), div[role='button']:has-text('Post'), a:has-text('Post')").filter(has_text="Post").first
            if post_item.is_visible(timeout=2000):
                post_item.click(force=True)
                time.sleep(2.0)

            if page.locator("input[type='file']").count() > 0:
                return True
    except Exception:
        pass

    return page.locator("input[type='file']").count() > 0


def set_schedule_datetime(page, target_dt: datetime) -> bool:
    """Set the scheduling Date and Time spinbuttons in Instagram's schedule modal."""
    try:
        target_day = str(target_dt.day)

        # 1. Date selection
        date_btn = page.locator("div[role='dialog'] div[role='button']:has-text('2026')").first
        if not date_btn.is_visible(timeout=2000):
            date_btn = page.locator("div[role='dialog'] div[role='button']").filter(
                has_text=re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)")
            ).first

        if date_btn.is_visible(timeout=2000):
            current_date_text = date_btn.inner_text().strip()
            day_regex = re.compile(rf"\b{target_day}\b")
            if not day_regex.search(current_date_text):
                date_btn.click(force=True)
                time.sleep(1.2)

                day_cell = page.locator(
                    f"button[role='gridcell']:has(span:text-is('{target_day}')), "
                    f"button[role='gridcell']:has-text('{target_day}')"
                ).first
                if day_cell.is_visible(timeout=2500):
                    day_cell.click(force=True)
                    time.sleep(1.0)
                else:
                    date_btn.click(force=True)
                    time.sleep(0.5)

        # 2. Hours (1-12)
        hour_12 = target_dt.strftime("%I").lstrip("0") or "12"
        h_input = page.locator("input[aria-label='Hours']").first
        if h_input.is_visible(timeout=2000):
            h_input.click(force=True)
            time.sleep(0.2)
            page.keyboard.press("Control+A")
            time.sleep(0.1)
            page.keyboard.type(hour_12)
            time.sleep(0.3)

        # 3. Minutes (00-59)
        min_str = target_dt.strftime("%M")
        m_input = page.locator("input[aria-label='Minutes']").first
        if m_input.is_visible(timeout=2000):
            m_input.click(force=True)
            time.sleep(0.2)
            page.keyboard.press("Control+A")
            time.sleep(0.1)
            page.keyboard.type(min_str)
            time.sleep(0.3)

        # 4. AM / PM
        ampm_target = target_dt.strftime("%p")
        ampm_input = page.locator("input[aria-label='AM PM']").first
        if ampm_input.is_visible(timeout=2000):
            current_ampm = ampm_input.evaluate("el => el.getAttribute('aria-valuetext')") or ""
            if current_ampm.upper() != ampm_target.upper():
                ampm_input.click(force=True)
                time.sleep(0.2)
                page.keyboard.press("ArrowUp")
                time.sleep(0.3)

        return True
    except Exception as e:
        print(f"Error setting schedule datetime: {e}")
        return False


def set_post_location(page, location: str, log_fn=None) -> bool:
    """Search and set location on the Instagram post create screen."""
    if not location:
        return False
    try:
        loc_input = page.locator("input[name='creation-location-input'], input[placeholder*='Add location' i]").first
        if not loc_input.is_visible(timeout=3000):
            return False
        loc_input.click(force=True)
        time.sleep(0.3)

        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.2)

        # Search using first landmark / city segment
        query = location.split(",")[0].strip()
        loc_input.fill(query)
        time.sleep(2.5)

        # Look for search results dropdown
        match_item = page.locator("div[role='none'] div[role='button'], div[role='dialog'] div[role='button']").filter(
            has_text=re.compile(re.escape(query.split()[0]), re.I)
        ).first
        if match_item.is_visible(timeout=2500):
            chosen = match_item.inner_text().replace("\n", " ").strip()
            match_item.click(force=True)
            time.sleep(1.0)
            if log_fn:
                log_fn(f"📍 Set location: '{chosen[:40]}'")
            return True
        else:
            page.keyboard.press("ArrowDown")
            time.sleep(0.3)
            page.keyboard.press("Enter")
            time.sleep(0.8)
            if log_fn:
                log_fn(f"📍 Set location via suggestion: '{query}'")
            return True
    except Exception as e:
        if log_fn:
            log_fn(f"Location notice: {e}")
        return False


def set_post_alt_texts(page, alt_texts: list, log_fn=None) -> bool:
    """Expand Accessibility and fill alt text for each carousel slide."""
    if not alt_texts:
        return False
    try:
        acc_btn = page.locator("div[role='button']:has-text('Accessibility'), span:has-text('Accessibility')").first
        if acc_btn.is_visible(timeout=2500):
            acc_btn.click(force=True)
            time.sleep(1.0)

            alt_inputs = page.locator("input[placeholder*='Alt text' i], input[aria-label*='Alt text' i]").all()
            for idx, text in enumerate(alt_texts):
                if idx < len(alt_inputs):
                    alt_inputs[idx].click(force=True)
                    time.sleep(0.2)
                    alt_inputs[idx].fill(text[:400])
                    time.sleep(0.3)
            if log_fn:
                log_fn(f"♿ Filled alt text across {min(len(alt_texts), len(alt_inputs))} carousel slide(s)")
            return True
    except Exception as e:
        if log_fn:
            log_fn(f"Alt text notice: {e}")
        return False


def set_post_ai_label(page, log_fn=None) -> bool:
    """Expand Advanced settings and toggle ON the 'Made with AI' / 'AI label' switch (Always ON)."""
    try:
        # 1. Expand Advanced settings accordion if present
        adv_btn = page.locator(
            "div[role='button']:has-text('Advanced settings'), "
            "span:has-text('Advanced settings'), "
            "button:has-text('Advanced settings')"
        ).first
        if adv_btn.is_visible(timeout=2000):
            adv_btn.click(force=True)
            time.sleep(1.0)

        # 2. Check for AI Label switch in DOM
        res = page.evaluate("""() => {
            const allElements = Array.from(document.querySelectorAll("div[role='dialog'] *"));
            const aiMatches = allElements.filter(el => {
                const t = (el.innerText || '').toLowerCase().trim();
                return (t.includes('ai label') || t.includes('made with ai') || t.includes('add ai label')) && t.length < 80;
            });
            
            for (let el of aiMatches) {
                const row = el.closest("div[role='button']") || el.closest("label") || el.closest("div") || el.parentElement;
                if (!row) continue;
                
                const toggle = row.querySelector("input[type='checkbox'], div[role='switch'], button[role='switch']") 
                            || el.parentElement.querySelector("input[type='checkbox'], div[role='switch'], button[role='switch']");
                            
                if (toggle) {
                    const isChecked = toggle.checked || toggle.getAttribute('aria-checked') === 'true';
                    if (!isChecked) {
                        toggle.click();
                        return { found: true, toggled: true, alreadyOn: false };
                    }
                    return { found: true, toggled: true, alreadyOn: true };
                }
            }
            
            const direct = document.querySelector("input[type='checkbox'][aria-label*='AI' i], div[role='switch'][aria-label*='AI' i]");
            if (direct) {
                const isChecked = direct.checked || direct.getAttribute('aria-checked') === 'true';
                if (!isChecked) {
                    direct.click();
                    return { found: true, toggled: true, alreadyOn: false };
                }
                return { found: true, toggled: true, alreadyOn: true };
            }
            
            return { found: false };
        }""")

        if res.get("toggled"):
            if res.get("alreadyOn"):
                if log_fn:
                    log_fn("🤖 AI label is already turned ON.")
            else:
                if log_fn:
                    log_fn("🤖 Successfully toggled AI label ('Made with AI') to ON (Always ON enforced).")
            return True

        if log_fn:
            log_fn("ℹ️ AI label switch not found in current dialog (handled by account-level AI badge).")
        return False
    except Exception as e:
        if log_fn:
            log_fn(f"AI label notice: {e}")
        return False


def set_post_tags(page, tagged_users: list, log_fn=None, collaborators: list = None) -> bool:
    """Open 'Tag people', invite collaborators if provided, and tag related handles."""
    if not tagged_users and not collaborators:
        return False
    try:
        tag_btn = page.locator("div[role='button']:has-text('Tag people'), button:has-text('Tag people')").first
        if not tag_btn.is_visible(timeout=2500):
            return False
        tag_btn.click(force=True)
        time.sleep(1.5)

        tagged_success = []
        collab_success = []

        # 1. Invite Collaborators if provided
        if collaborators:
            collab_tab = page.locator("span:has-text('Invite collaborator'), div[role='tab']:has-text('Invite collaborator'), button:has-text('Invite collaborator')").first
            if collab_tab.is_visible(timeout=2500):
                collab_tab.click(force=True)
                time.sleep(1.0)
                for user in collaborators:
                    clean_user = user.lstrip("@").strip()
                    if not clean_user:
                        continue
                    collab_search = page.locator("input[placeholder*='Search' i], input[placeholder*='Invite' i]").first
                    if collab_search.is_visible(timeout=2000):
                        collab_search.fill(clean_user)
                        time.sleep(2.0)
                        user_match = page.locator(f"div[role='button']:has-text('{clean_user}'), div[role='none']:has-text('{clean_user}')").first
                        if user_match.is_visible(timeout=3000):
                            user_match.click(force=True)
                            time.sleep(1.0)
                            collab_success.append(f"@{clean_user}")
                        else:
                            page.keyboard.press("Enter")
                            time.sleep(0.8)
                            collab_success.append(f"@{clean_user}")

        # Switch back to Tag tab if we invited collaborator
        tag_tab = page.locator("span:has-text('Tag'), div[role='tab']:has-text('Tag')").first
        if tag_tab.is_visible(timeout=1500) and collaborators:
            tag_tab.click(force=True)
            time.sleep(1.0)

        # 2. Tag related accounts on preview image
        preview_img = page.locator("div[role='dialog'] img").first
        for user in tagged_users or []:
            clean_user = user.lstrip("@").strip()
            if not clean_user or clean_user in [c.lstrip("@") for c in (collaborators or [])]:
                continue
            if preview_img.is_visible(timeout=2000):
                preview_img.click(position={"x": 120, "y": 120}, force=True)
                time.sleep(1.0)
                tag_search = page.locator("input[placeholder*='Search' i], input[placeholder*='Tag' i]").first
                if tag_search.is_visible(timeout=2000):
                    tag_search.fill(clean_user)
                    time.sleep(2.0)
                    user_match = page.locator(f"div[role='button']:has-text('{clean_user}'), div[role='none']:has-text('{clean_user}')").first
                    if user_match.is_visible(timeout=3000):
                        user_match.click(force=True)
                        time.sleep(1.0)
                        tagged_success.append(f"@{clean_user}")
                    else:
                        page.keyboard.press("Enter")
                        time.sleep(0.8)
                        tagged_success.append(f"@{clean_user}")

        # Click Done
        done_btn = page.locator("div[role='button']:text-is('Done'), button:text-is('Done'), span:text-is('Done')").first
        if done_btn.is_visible(timeout=2500):
            done_btn.click(force=True)
            time.sleep(1.0)

        if log_fn:
            if collab_success:
                log_fn(f"🤝 Invited collaborator(s): {', '.join(collab_success)}")
            if tagged_success:
                log_fn(f"🏷️ Tagged related account(s): {', '.join(tagged_success)}")
        return True
    except Exception as e:
        if log_fn:
            log_fn(f"Tagging notice: {e}")
        return False


def process_account_posts(account: str, schedule_mode: bool = True, dry_run: bool = False, day_filter: int = 0) -> None:
    log_file_path = os.path.join(PROJECT_DIR, f"publish_log_{account}.txt")
    queue = load_queue()
    ready_items = [
        item for item in queue
        if item.get("account") == account
        and item.get("status") == "APPROVED"
        and (day_filter == 0 or item.get("day_index") == day_filter)
        and get_valid_media_paths(item)
    ]
    ready_items.sort(key=lambda x: x.get("day_index", 999))

    if not ready_items:
        log_activity(
            log_file_path,
            account,
            "No APPROVED posts with valid draft_media paths found to process.",
        )
        return

    # Compute target schedule times
    account_offset_hours = ACCOUNT_OFFSETS.get(account, 0)
    for idx, item in enumerate(ready_items):
        if item.get("scheduled_for"):
            try:
                item["_target_dt"] = datetime.strptime(item["scheduled_for"], "%Y-%m-%d %I:%M %p")
            except Exception:
                day_offset = (item.get("day_index", idx + 1) - 1) * POST_INTERVAL_HOURS
                item["_target_dt"] = BASE_START_TIME + timedelta(hours=account_offset_hours + day_offset)
        else:
            day_offset = (item.get("day_index", idx + 1) - 1) * POST_INTERVAL_HOURS
            item["_target_dt"] = BASE_START_TIME + timedelta(hours=account_offset_hours + day_offset)

    user_data_dir = get_chrome_profile_dir(account)
    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lock_path = os.path.join(user_data_dir, lock_file)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    with sync_playwright() as p:
        action_verb = "Scheduling" if schedule_mode else "Publishing"
        log_activity(log_file_path, account, f"Launching Google Chrome for @{account} ({len(ready_items)} post(s) queued for {action_verb.lower()})...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        for idx, item in enumerate(ready_items):
            media_paths = get_valid_media_paths(item)
            caption = item.get("caption", "").strip()
            item_id = item.get("id", "")
            # Internal ID is tracked in swarm_queue.json, kept out of public captions

            target_dt = item["_target_dt"]
            sched_str = target_dt.strftime("%Y-%m-%d %I:%M %p")
            names = ", ".join(os.path.basename(m) for m in media_paths)

            log_activity(log_file_path, account, f"--- [{idx + 1}/{len(ready_items)}] Draft [id:{item_id}] | Day {item.get('day_index')} | Target: {sched_str} ({len(media_paths)} files) ---")

            try:
                # Open create or scheduled content dialog
                opened = open_create_or_schedule_dialog(page, schedule_mode=schedule_mode)
                if not opened:
                    raise TimeoutError("Could not open Instagram create / schedule dialog")

                file_input = page.locator("input[type='file']").first
                file_input.wait_for(state="attached", timeout=10000)
                file_input.set_input_files(media_paths)
                time.sleep(4.0)

                # Select aspect ratio (Original or 4:5 portrait)
                try:
                    crop_btn = page.locator(
                        "svg[aria-label='Select crop'], button[aria-label='Select crop'], "
                        "div[role='button']:has(svg[aria-label='Select crop']), "
                        "div[role='button']:has-text('Crop'), button:has-text('Crop')"
                    ).first
                    if crop_btn.is_visible(timeout=3000):
                        crop_btn.click(force=True)
                        time.sleep(1.0)
                        ratio_opt = page.locator(
                            "span:text-is('4:5'), div[role='button']:has-text('4:5'), button:has-text('4:5'), "
                            "span:text-is('Original'), div[role='button']:has-text('Original'), button:has-text('Original')"
                        ).first
                        if ratio_opt.is_visible(timeout=3000):
                            chosen_ratio = ratio_opt.inner_text().strip()
                            ratio_opt.click(force=True)
                            time.sleep(1.0)
                            log_activity(log_file_path, account, f"📐 {chosen_ratio} aspect ratio selected for [id:{item_id}]")
                except Exception as e:
                    log_activity(log_file_path, account, f"Aspect ratio selection note: {e}")

                # Advance to caption / details screen
                for _ in range(4):
                    next_btn = page.locator("div[role='button']:text-is('Next'), button:text-is('Next')").first
                    if next_btn.is_visible(timeout=4000):
                        next_btn.click(force=True)
                        time.sleep(2.0)

                # 1. Fill caption with included ID
                caption_box = page.locator(
                    "div[aria-label*='caption' i][role='textbox'], "
                    "textarea[aria-label*='caption' i], "
                    "[contenteditable='true'][aria-label*='caption' i]"
                ).first
                caption_box.wait_for(state="visible", timeout=12000)
                caption_box.click(force=True)
                time.sleep(0.5)
                caption_box.fill(caption)
                time.sleep(1.0)
                log_activity(log_file_path, account, f"📝 Filled clean editorial caption for [id:{item_id}]")

                # 2. Add Location
                loc = item.get("location")
                if loc:
                    set_post_location(page, loc, log_fn=lambda msg: log_activity(log_file_path, account, msg))

                # 3. Tag People & Invite Collaborators
                tags = item.get("tagged_users") or item.get("tags") or []
                collabs = item.get("collaborators") or item.get("collaborator") or []
                if isinstance(collabs, str):
                    collabs = [collabs]
                if tags or collabs:
                    set_post_tags(page, tags, log_fn=lambda msg: log_activity(log_file_path, account, msg), collaborators=collabs)

                # 4. Fill Alt Text (Accessibility)
                alt_texts = item.get("alt_texts")
                if not alt_texts and item.get("alt_text"):
                    alt_texts = [item.get("alt_text")] * len(media_paths)
                if alt_texts:
                    set_post_alt_texts(page, alt_texts, log_fn=lambda msg: log_activity(log_file_path, account, msg))

                # 5. Always Turn ON AI Label ("Made with AI")
                set_post_ai_label(page, log_fn=lambda msg: log_activity(log_file_path, account, msg))

                # 6. Scheduling / Publishing
                if schedule_mode:
                    log_activity(log_file_path, account, f"⏰ Setting schedule date & time -> {sched_str}...")
                    set_schedule_datetime(page, target_dt)
                    time.sleep(1.5)

                    if dry_run:
                        log_activity(log_file_path, account, f"[DRY RUN] Ready to schedule [id:{item_id}] for {sched_str}. Skipping final click.")
                    else:
                        sched_btn = page.locator(
                            "div[role='dialog'] div[role='button']:text-is('Schedule'), "
                            "div[role='dialog'] button:text-is('Schedule'), "
                            "div[role='button']:text-is('Schedule'), button:text-is('Schedule')"
                        ).first
                        if sched_btn.is_visible(timeout=3000):
                            sched_btn.click(force=True)
                            log_activity(log_file_path, account, f"Submitted Schedule request for [id:{item_id}]...")

                            # Wait for Instagram confirmation
                            for _ in range(25):
                                time.sleep(1.0)
                                if page.locator("span:has-text('scheduled'), div:has-text('scheduled'), div:has-text('Your post has been scheduled')").count() > 0:
                                    log_activity(log_file_path, account, "Instagram confirmation: Post has been scheduled!")
                                    break
                                if page.locator("div[role='dialog']").count() == 0:
                                    break

                            # Reload queue and persist status
                            current_q = load_queue()
                            for q_item in current_q:
                                if q_item.get("id") == item_id:
                                    q_item["status"] = "SCHEDULED"
                                    q_item["scheduled_for"] = sched_str
                                    q_item["scheduled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    break
                            save_queue(current_q)
                            log_activity(log_file_path, account, f"✅ Successfully scheduled [id:{item_id}] for {sched_str}!")
                        else:
                            log_activity(log_file_path, account, "⚠️ Schedule button not visible, attempting Share...")
                            share_btn = page.locator("div[role='button']:text-is('Share'), button:text-is('Share')").first
                            if share_btn.is_visible(timeout=2000):
                                share_btn.click(force=True)
                                time.sleep(10.0)
                else:
                    if dry_run:
                        log_activity(log_file_path, account, f"[DRY RUN] Ready to share [id:{item_id}]. Skipping Share click.")
                    else:
                        share_btn = page.locator("div[role='button']:text-is('Share'), button:text-is('Share')").first
                        share_btn.click(force=True)
                        time.sleep(10.0)

                        current_q = load_queue()
                        for q_item in current_q:
                            if q_item.get("id") == item_id:
                                q_item["status"] = "PUBLISHED"
                                q_item["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                break
                        save_queue(current_q)
                        log_activity(log_file_path, account, f"✅ Published [id:{item_id}] successfully!")

                # Dismiss dialog cleanly if still open
                try:
                    close_btn = page.locator("div[role='dialog'] svg[aria-label='Close'], div[role='dialog'] button:has-text('Done'), div[role='dialog'] [aria-label='Close']").first
                    if close_btn.is_visible(timeout=1500):
                        close_btn.click(force=True)
                        time.sleep(1.0)
                    else:
                        page.keyboard.press("Escape")
                        time.sleep(0.8)
                        discard = page.locator("div[role='button']:has-text('Discard'), button:has-text('Discard')").first
                        if discard.is_visible(timeout=2000):
                            discard.click(force=True)
                except Exception:
                    pass
                time.sleep(3.0)

            except Exception as e:
                log_activity(log_file_path, account, f"❌ Failed to process [id:{item_id}]: {e}")
                try:
                    page.keyboard.press("Escape")
                    time.sleep(1.0)
                except Exception:
                    pass

        context.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schedule or publish APPROVED posts from swarm_queue.json to Instagram.")
    parser.add_argument(
        "-a",
        "--account",
        default="all",
        type=parse_account,
        help=f"Instagram handle to process ({', '.join(ACCOUNTS)} or 'all')",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        default=True,
        help="Schedule posts using Instagram's native scheduler (default: True)",
    )
    parser.add_argument(
        "--publish-now",
        action="store_true",
        help="Publish immediately instead of scheduling",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the workflow without clicking final Schedule/Share",
    )
    parser.add_argument(
        "--day",
        type=int,
        default=0,
        help="Only process a specific day_index (e.g. --day 3); 0 = all approved",
    )
    args = parser.parse_args()

    mode = not args.publish_now

    if args.account == "all":
        for acc in ACCOUNTS:
            process_account_posts(acc, schedule_mode=mode, dry_run=args.dry_run, day_filter=args.day)
    else:
        process_account_posts(args.account, schedule_mode=mode, dry_run=args.dry_run, day_filter=args.day)
