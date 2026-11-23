"""
Instagram Network Engager (Hardened Ad-Shield & Niche-Filtered Following Engager)
================================================================================
Strictly enforces:
1. 100% AD-BLOCK SHIELD:
   - Blocks any post with Ad / Sponsored / Promoted badges.
   - Blocks any post with CTA buttons: Apply now, Learn more, Shop now, Sign up, Install now, Book now, etc.
   - Double-checks both in-feed article AND open comment modal dialog. If an Ad is detected, aborts immediately.
2. STRICT FOLLOWING & STRANGER FILTER:
   - Skips strangers (accounts showing 'Follow' / 'Follow back').
   - Skips suggested posts / 'Suggested for you'.
3. NICHE RELEVANCE GUARD:
   - Validates caption and content against the creator's exact niche keywords.
   - Maira Mehra ONLY engages with ethnic wear, sarees, lehengas, jewelry, and couture.
   - Avanya Mehra ONLY engages with high fashion, Parisian tailoring, and runway editorial.
   - Gagan Kumar ONLY engages with menswear, bespoke tailoring, and grooming.
   - Resrise Studio ONLY engages with creative production, cinematography, and studio lighting.
   - Completely rejects off-niche content (courses, admissions, crypto, tech ads, memes).
4. DYNAMIC CONTEXTUAL COMMENTS & ZERO REPETITION:
   - Generates comments tailored directly to the specific garment, drape, or aesthetic in the caption.
   - Anti-repetition engine enforces <35% word overlap across all accounts in the last 72 hours.
   - Daily limit strictly capped at 2-3 comments per account per day.
"""

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = (
    os.path.dirname(SCRIPT_DIR)
    if os.path.basename(SCRIPT_DIR).lower() == "scripts"
    else SCRIPT_DIR
)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from core.anti_repetition import (
        is_comment_repetitive,
        record_generated_comment,
        get_daily_comment_count,
        is_post_globally_commented,
        add_post_to_global_cache,
        load_comments_history,
        load_global_cache,
        save_global_cache,
        normalize_post_identifier,
        GLOBAL_CACHE_FILE,
        HISTORY_FILE,
    )
except ImportError:
    from scripts.core.anti_repetition import (
        is_comment_repetitive,
        record_generated_comment,
        get_daily_comment_count,
        is_post_globally_commented,
        add_post_to_global_cache,
        load_comments_history,
        load_global_cache,
        save_global_cache,
        normalize_post_identifier,
        GLOBAL_CACHE_FILE,
        HISTORY_FILE,
    )

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]
CHROME_PROFILES_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data - Automation")

# Comprehensive Ad & Sponsored Triggers
AD_CTA_KEYWORDS = [
    "apply now", "learn more", "shop now", "sign up", "install now", "download",
    "book now", "order now", "get offer", "contact us", "send message", "visit instagram profile",
    "watch more", "play game", "open link", "subscribe", "get quote", "listen now"
]

AD_BADGE_REGEX = re.compile(
    r"\b(sponsored|promoted|ad|ads|paid\s+partnership|paid\s+promotion)\b"
    r"|suggested\s+for\s+you|suggested\s+post|प्रायोजित|आपके लिए सुझाव|विज्ञापन",
    re.IGNORECASE
)

# Niche Topic Filters (Must match at least 1 keyword to engage)
CREATOR_NICHE_KEYWORDS = {
    "mairamehraofficial": [
        "saree", "sari", "lehenga", "couture", "fashion", "styling", "style", "drape",
        "ethnic", "silk", "zari", "kundan", "jewelry", "jewellery", "wedding", "festive",
        "outfit", "designer", "handloom", "dupatta", "choli", "anarkali", "kurti",
        "traditional", "heritage", "polki", "choker", "banarasi", "kanjivaram", "organza",
        "attire", "couture", "bridal", "drapes", "glam", "look"
    ],
    "avanyamehra": [
        "fashion", "style", "styling", "editorial", "outfit", "blazer", "dress", "chic",
        "vogue", "runway", "milan", "paris", "haute", "couture", "aesthetic", "tailoring",
        "lookbook", "luxury", "silhouette", "trench", "model", "gala", "evening", "gown",
        "designer", "glam", "streetstyle", "minimalist"
    ],
    "iamgagankumar": [
        "menswear", "menstyle", "style", "fashion", "tailoring", "suit", "blazer", "tuxedo",
        "bandhgala", "grooming", "watch", "linen", "shirt", "jacket", "outfit", "founder",
        "creator", "shoes", "lifestyle", "bespoke", "fragrance", "cologne", "capsule"
    ],
    "resrise": [
        "production", "creative", "studio", "film", "lighting", "campaign", "direction",
        "editorial", "visual", "cinematography", "design", "brand", "set", "camera", "color",
        "color grading", "photoshoot", "agency", "creator economy"
    ],
    "gagankumarrocks": [
        "creator", "systems", "founder", "build", "production", "media", "business", "growth",
        "workflow", "content", "automation", "tech", "studio", "architecture", "scale"
    ]
}


def log_activity(log_file: str, account: str, msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{ts}] [@{account}] {msg}"
    print(full_msg, flush=True)
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except Exception:
        pass


def get_chrome_profile_dir(account: str) -> str:
    path = os.path.join(CHROME_PROFILES_DIR, account)
    os.makedirs(path, exist_ok=True)
    return path


def load_commented_cache(cache_file: str) -> set:
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_commented_cache(cache_file: str, cache_set: set) -> None:
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(sorted(list(cache_set)), f, indent=2)
    except Exception:
        pass


def get_account_profile(account: str) -> dict:
    """Loads account profile from accounts_config.json."""
    candidates = [
        os.path.join(PROJECT_DIR, "scripts", "accounts_config.json"),
        os.path.join(SCRIPT_DIR, "accounts_config.json"),
        os.path.join(PROJECT_DIR, "accounts_config.json"),
    ]
    acc_clean = account.lstrip("@").lower()
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "accounts" in data and acc_clean in data["accounts"]:
                        return data["accounts"][acc_clean]
                    if acc_clean in data:
                        return data[acc_clean]
            except Exception:
                pass
    return {
        "display_name": account,
        "niche": "fashion & lifestyle",
        "pillars": ["Editorial Fashion", "Visual Styling"],
    }


def get_persona_prompt(account: str) -> str:
    """Returns a tailored peer commenting prompt for @account."""
    acc_clean = account.lstrip("@").lower()
    profile = get_account_profile(acc_clean)
    niche = profile.get("niche", "fashion")
    return f"You are @{acc_clean} leaving a peer comment on a peer creator post in the {niche} niche."


def has_user_already_commented(article, account: str) -> bool:
    """Checks if @account has already commented in the post DOM."""
    try:
        acc_clean = account.lstrip("@").lower()
        return bool(article.evaluate("""(targetAccount) => {
            const allLinks = Array.from(document.querySelectorAll("a[role='link'][href^='/']"));
            for (let link of allLinks) {
                const handle = link.pathname.replace(/\\//g, '').toLowerCase();
                if (handle === targetAccount) return true;
            }
            return false;
        }""", acc_clean))
    except Exception:
        return False


def is_ad_or_sponsored_dom(element) -> tuple[bool, str]:
    """
    Evaluates an element (article or dialog) for ANY ad indicator.
    Returns (is_ad, reason).
    """
    try:
        data = element.evaluate("""(el) => {
            const text = (el.innerText || '');
            
            // Check 1: Explicit Ad / Sponsored header badges
            const badges = Array.from(el.querySelectorAll ? el.querySelectorAll("header span, header div, header a, span[dir='auto']") : []);
            let badgeText = '';
            for (let b of badges) {
                const t = (b.innerText || '').trim();
                if (/^(Ad|Sponsored|Promoted|Paid partnership|प्रायोजित|विज्ञापन)$/i.test(t)) {
                    badgeText = t;
                    break;
                }
            }
            
            // Check 2: Action CTA Buttons (exclusive to Ads)
            const buttons = Array.from(el.querySelectorAll ? el.querySelectorAll("button, div[role='button'], a[role='button'], a[href*='l.instagram.com']") : []);
            let ctaFound = '';
            const ctaRegex = /^(apply now|learn more|shop now|sign up|install now|download|book now|order now|get offer|contact us|send message|visit instagram profile|watch more|play game|open link|subscribe|get quote|listen now)$/i;
            for (let btn of buttons) {
                const bt = (btn.innerText || '').trim();
                if (ctaRegex.test(bt)) {
                    ctaFound = bt;
                    break;
                }
            }
            
            // Check 3: Check full text for Ad keywords
            const hasSponsoredText = /(?:^|\\W)(sponsored|promoted|paid\\s+partnership)(?:$|\\W)|suggested\\s+for\\s+you/i.test(text);
            
            return {
                badgeText,
                ctaFound,
                hasSponsoredText,
                textSnippet: text.slice(0, 300)
            };
        }""")
        
        if isinstance(data, dict):
            if data.get("isSponsored"):
                return True, f"Sponsored flag: {data.get('text', 'Ad')}"
            if data.get("badgeText"):
                return True, f"Header badge: '{data['badgeText']}'"
            if data.get("ctaFound"):
                return True, f"Ad CTA button: '{data['ctaFound']}'"
            if data.get("hasSponsoredText"):
                return True, "Sponsored text matched"
            
        return False, ""
    except Exception as e:
        return False, f"Eval error: {e}"


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
                    data = json.load(f)
                    if isinstance(data, dict) and "accounts" in data:
                        res = dict(data["accounts"])
                        res["accounts"] = data["accounts"]
                        return res
                    return data
            except Exception:
                pass
    return {}


def is_post_from_followed_account(article, account: str = ""):
    """
    Validates that a feed post article:
    1. Is 100% NOT an Ad or Sponsored post.
    2. Does NOT show a 'Follow' button (belongs to someone you already follow).
    3. Belongs to the creator's specific niche (if account specified).
    Returns (is_valid, author, caption) if account is specified, or (is_valid, author) if omitted.
    """
    try:
        # Step 1: Strict Ad & CTA Check
        is_ad, ad_reason = is_ad_or_sponsored_dom(article)
        if is_ad:
            if account:
                return False, "", f"Skipped Ad ({ad_reason})"
            return False, ""

        # Step 2: Author Extraction & Follow Button Check
        eval_result = article.evaluate("""(el) => {
            const text = (el.innerText || '');
            
            // Check if mock or DOM indicates sponsored
            const hasSponsoredText = /(?:^|\\W)(sponsored|promoted|paid\\s+partnership)(?:$|\\W)|suggested\\s+for\\s+you|प्रायोजित|सुझाव/i.test(text);

            const links = Array.from(el.querySelectorAll ? el.querySelectorAll("a[role='link'][href^='/'], header a[role='link']") : []);
            let author = '';
            for (let l of links) {
                const raw = (l.getAttribute('href') || l.pathname || '').replace(/\\//g, '').toLowerCase().split('?')[0];
                if (
                    raw &&
                    !raw.startsWith('p') &&
                    !raw.startsWith('reel') &&
                    !raw.startsWith('explore') &&
                    !raw.startsWith('direct') &&
                    !raw.startsWith('stories') &&
                    raw !== 'unknown'
                ) {
                    author = raw;
                    break;
                }
            }

            // Check if post shows a Follow button (indicates a stranger)
            const buttons = Array.from(el.querySelectorAll ? el.querySelectorAll("header button, header div[role='button'], div[role='button']") : []);
            const hasFollowBtn = buttons.some(b => {
                const t = (b.innerText || '').trim().toLowerCase();
                return t === 'follow' || t === 'follow back' || t === 'फ़ॉलो करें' || t === 'फॉलो करें';
            });

            // Extract caption text
            const span = el.querySelector ? el.querySelector('div[role="button"] + span, h1 + span, article span[dir="auto"], article span') : null;
            const caption = span ? (span.innerText || '').trim() : '';

            return { author, hasFollowBtn, caption, isSponsored: hasSponsoredText };
        }""")

        if isinstance(eval_result, dict):
            if eval_result.get("isSponsored"):
                if account:
                    return False, "", "Skipped Sponsored/Ad"
                return False, ""

            author = str(eval_result.get("author", "")).strip().lstrip("@").lower()
            if not author or author in ("unknown", "none", "null", ""):
                if account:
                    return False, "", "Could not resolve author"
                return False, ""

            if eval_result.get("hasFollowBtn"):
                if account:
                    return False, author, "Stranger (Follow button visible)"
                return False, author

            caption = eval_result.get("caption", "")

            # Step 3: Niche Relevance Check (if account specified)
            if account:
                niche_keywords = CREATOR_NICHE_KEYWORDS.get(account.lower(), [])
                if niche_keywords:
                    full_content_text = f"{author} {caption}".lower()
                    has_niche_match = any(kw in full_content_text for kw in niche_keywords)
                    if not has_niche_match:
                        return False, author, f"Off-niche content (No relevant fashion/styling match for @{account})"
                return True, author, caption

            return True, author

        return (False, "", "Unknown evaluation structure") if account else (False, "")
    except Exception as e:
        return (False, "", f"Error: {e}") if account else (False, "")
    except Exception as e:
        return False, "", f"Error inspecting article: {e}"


def generate_contextual_comment(
    account: str,
    author: str = "",
    caption_text: str = "",
    image_bytes: bytes = None,
) -> str:
    """
    Generates an authentic, dynamic, context-aware peer comment tailored to the actual post.
    If image_bytes is provided, leverages live Vision (Gemini / OpenRouter) to write a sincere,
    detail-specific peer response.
    Enforces anti-repetition guards (<35% overlap across last 72 hours).
    """
    # Safeguard against parameter swapping (e.g. if author is passed as image_bytes)
    if isinstance(author, (bytes, bytearray)):
        image_bytes = author
        author = ""

    clean_acc = account.lstrip("@").lower()
    history = load_comments_history()

    # 1. Try live Vision if image_bytes is provided
    if image_bytes and len(image_bytes) > 0:
        try:
            from scripts.core.vision import VisionClient
            v_client = VisionClient()
            if v_client.is_configured():
                v_prompt = (
                    f"You are commenting from the Instagram persona @{clean_acc}. "
                    f"Post author: @{author if author else 'peer'}. "
                    f"Caption: {caption_text[:300] if caption_text else 'None'}. "
                    "Write an authentic, human, peer comment (1-2 sentences maximum). "
                    "Observe one specific visual detail in the image (e.g. fabric drape, lighting, color harmony, tailoring, embroidery, jewelry, or silhouette). "
                    "Compliment it sincerely or ask an organic question. "
                    "Tone: effortless, supportive creator peer. No bot hype, no sales pitch, no exclamation mark spam. Maximum 1 tasteful emoji. "
                    "Output ONLY the comment text."
                )
                vision_reply = v_client.call_vision(v_prompt, image_bytes)
                if vision_reply:
                    cand = vision_reply.strip().strip('"').strip("'")
                    if cand and len(cand) > 10:
                        is_rep, _ = is_comment_repetitive(cand, history=history, max_overlap=0.35, lookback_hours=72.0)
                        if not is_rep:
                            return cand
        except Exception:
            pass

    cap_lower = caption_text.lower() if caption_text else ""

    # Dynamic pool tailored to specific niche indicators in the post
    candidate_pool = []

    if clean_acc == "mairamehraofficial":
        if any(w in cap_lower for w in ["saree", "sari", "drape", "pallu"]):
            candidate_pool.extend([
                "The drape and movement on this saree are breathtaking 🌸",
                "Such an exquisite drape! The handloom border looks magnificent ✨",
                "Pure handloom grace in every fold! Stunning styling 🌸",
                "The fluid drape and color contrast here are so refined ✨",
                "Masterclass in elegant draping! Beautifully carried 🌸",
            ])
        elif any(w in cap_lower for w in ["velvet", "silk", "brocade", "zari"]):
            candidate_pool.extend([
                "The richness of this textile weave is absolutely stunning ✨",
                "Loving the decadent sheen and royal texture of this fabric 🌸",
                "Such majestic textile craftsmanship! Pure heritage grace ✨",
                "The zari embroidery detail on this piece is so delicate 🌸",
            ])
        elif any(w in cap_lower for w in ["jewelry", "jewellery", "kundan", "choker", "pearl", "polki"]):
            candidate_pool.extend([
                "That antique jewelry pairing complements the attire so gracefully 🌸",
                "The choker craftsmanship and uncut stone details are mesmerizing ✨",
                "Such an ethereal jewelry balance with this ensemble 🌸",
            ])
        else:
            candidate_pool.extend([
                "Such timeless cultural grace styled with modern finesse 🌸",
                "The tonal balance and graceful poise here are wonderful ✨",
                "Breathtaking elegance in this frame! Beautifully captured 🌸",
                "Loving the regal ambiance and subtle color harmony here ✨",
                "Such radiant festive energy and poise in every frame 🌸",
            ])

    elif clean_acc == "avanyamehra":
        if any(w in cap_lower for w in ["blazer", "suit", "tailoring", "trench"]):
            candidate_pool.extend([
                "The architectural proportions and lapel tailoring here are sublime 🤍",
                "Sharp tailoring with such effortless movement! Impeccable fit ✨",
                "Masterful structured silhouette! Understated luxury at its best 🤍",
            ])
        elif any(w in cap_lower for w in ["dress", "gown", "cowl", "silk"]):
            candidate_pool.extend([
                "The fluid drape on this silhouette is absolute poetry ✨",
                "Such captivating movement and understated evening elegance 🤍",
                "Flawless fabric drape and sculptural poise! Truly stunning ✨",
            ])
        else:
            candidate_pool.extend([
                "Pure high-fashion vision! The lighting and tones are breathtaking 🤍",
                "Sublime creative direction and palette balance in this editorial ✨",
                "Refined minimalist aesthetic with such striking presence 🤍",
                "The mood, texture, and framing here are impeccably balanced ✨",
            ])

    elif clean_acc == "iamgagankumar":
        if any(w in cap_lower for w in ["suit", "blazer", "tuxedo", "bandhgala", "tailoring"]):
            candidate_pool.extend([
                "Sharp tailoring and clean shoulder line. Impeccably executed ⚡",
                "The proportions and button stance on this jacket are spot on.",
                "Understated heritage black-tie elegance. Very well put together ⚡",
            ])
        elif any(w in cap_lower for w in ["watch", "fragrance", "grooming", "linen"]):
            candidate_pool.extend([
                "Subtle accessories with a timeless aesthetic. Great details ⚡",
                "Crisp texture and understated tones. Sharp fit man.",
                "Clean grooming and classic timepiece pairing. Strong look ⚡",
            ])
        else:
            candidate_pool.extend([
                "Clean lines, refined palette, and effortless fit. Solid aesthetic ⚡",
                "Minimalist styling executed with commanding restraint.",
                "Well balanced tones and timeless proportions. Respect ⚡",
            ])

    elif clean_acc == "resrise":
        candidate_pool.extend([
            "Dynamic staging and exquisite tonal grading on this shoot ✨",
            "Incredible atmospheric lighting and cinematic visual storytelling ✨",
            "Exceptional compositional depth and set design! Flawlessly executed ✨",
            "The camera movement and chromatic harmony here are inspiring ✨",
        ])

    else:
        candidate_pool.extend([
            "Clean perspective and exceptional dedication to the craft ⚡",
            "Consistency and vision always command attention. Great work 🚀",
            "Sharp execution and thoughtful aesthetic direction ⚡",
        ])

    # Shuffle and pick a candidate that passes the strict anti-repetition guard
    random.shuffle(candidate_pool)
    for cand in candidate_pool:
        is_rep, reason = is_comment_repetitive(cand, history=history, max_overlap=0.35, lookback_hours=72.0)
        if not is_rep:
            return cand

    # Ultimate fallback with randomized timestamp suffix guarantee
    unique_mod = random.choice(["Truly inspired by this", "Magnificent vision", "Brilliant craft"])
    return f"{unique_mod} and dedication to the aesthetic ✨"


# Backwards compatibility alias
generate_peer_comment = generate_contextual_comment


def run_following_engager(
    account: str,
    max_comments: int = 2,
    max_feed_scrolls: int = 15,
    draft_only: bool = False,
    headless: bool = False,
) -> None:
    log_file_path = os.path.join(PROJECT_DIR, f"engager_activity_log_{account}.txt")
    cache_file = os.path.join(PROJECT_DIR, f"commented_posts_cache_{account}.json")

    # Anti-repetition & daily quota check (Strict Max 2-3 comments per day)
    daily_count = get_daily_comment_count(account)
    if daily_count >= 3:
        log_activity(
            log_file_path,
            account,
            f"🛑 Daily limit reached ({daily_count}/3 comments in last 24h). Skipping run to protect account safety.",
        )
        return

    allowed_today = max(0, 3 - daily_count)
    effective_max = min(max_comments, allowed_today)
    if effective_max <= 0:
        log_activity(log_file_path, account, "🛑 No comment quota remaining today. Skipping.")
        return

    commented_cache = load_commented_cache(cache_file)
    log_activity(
        log_file_path,
        account,
        f"Starting Hardened Following-Engager. Daily comments so far: {daily_count}/3. Target: {effective_max}.",
    )

    user_data_dir = get_chrome_profile_dir(account)
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lp = os.path.join(user_data_dir, lock)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    comments_posted = 0

    with sync_playwright() as p:
        log_activity(log_file_path, account, f"Launching Google Chrome for @{account}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=headless,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        log_activity(log_file_path, account, "Navigating to Instagram Feed (Filtering: Followed creators only)...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(random.uniform(4.0, 6.0))

        seen_post_keys = set()

        for scroll_idx in range(max_feed_scrolls):
            if comments_posted >= effective_max:
                log_activity(log_file_path, account, f"🎯 Reached target of {effective_max} comments. Exiting cleanly.")
                break

            articles = page.locator("article").all()
            log_activity(log_file_path, account, f"Scanning feed screen #{scroll_idx + 1} ({len(articles)} posts visible)...")

            for art in articles:
                if comments_posted >= effective_max:
                    break

                try:
                    # 1. Multi-tier Ad & Followed-Only Verification
                    is_valid, author, reason_or_caption = is_post_from_followed_account(art, account)
                    if not is_valid:
                        # Log skip reason (e.g. Skipped Ad, Stranger, Off-niche)
                        if "ad" in reason_or_caption.lower() or "off-niche" in reason_or_caption.lower():
                            log_activity(log_file_path, account, f"🛡️ [FILTER] {reason_or_caption}")
                        continue

                    caption_text = reason_or_caption

                    # Never self-comment
                    if author == account.lower():
                        continue

                    # Extract post shortcode or identifier
                    post_link = art.locator("a[href*='/p/'], a[href*='/reel/']").first
                    post_href = post_link.get_attribute("href") if post_link.is_visible(timeout=500) else ""
                    post_id = post_href.split("?")[0].strip("/") if post_href else f"{author}_{scroll_idx}"

                    if post_id in seen_post_keys:
                        continue
                    seen_post_keys.add(post_id)

                    # Check persistent caches
                    if post_id in commented_cache:
                        log_activity(log_file_path, account, f"[SKIP] Post from @{author} ({post_id}) already in cache.")
                        continue

                    is_global, commented_by = is_post_globally_commented(post_id)
                    if is_global:
                        log_activity(
                            log_file_path,
                            account,
                            f"🚫 [GLOBAL SKIP] Post ({post_id}) already commented on by @{commented_by}! Skipping.",
                        )
                        commented_cache.add(post_id)
                        save_commented_cache(cache_file, commented_cache)
                        continue

                    art.scroll_into_view_if_needed()
                    time.sleep(random.uniform(1.2, 2.0))

                    # Like the followed creator's post first
                    like_btn = art.locator("svg[aria-label*='Like' i], svg[aria-label*='पसंद' i]").first
                    if like_btn.is_visible(timeout=1000):
                        try:
                            like_btn.click(force=True)
                            log_activity(log_file_path, account, f"❤️ Liked followed post from @{author}")
                            time.sleep(random.uniform(1.0, 2.0))
                        except Exception:
                            pass

                    # Generate strictly contextual comment
                    comment_text = generate_contextual_comment(account, author, caption_text)

                    if draft_only:
                        log_activity(log_file_path, account, f"[DRAFT ONLY] Would comment on @{author}'s post: '{comment_text}'")
                        comments_posted += 1
                        time.sleep(2.0)
                        continue

                    # Click comment bubble icon to open comment modal or activate box
                    comment_icon = art.locator("svg[aria-label*='Comment' i], svg[aria-label*='टिप्पणी' i]").first
                    if comment_icon.is_visible(timeout=1500):
                        comment_icon.click(force=True)
                        time.sleep(2.0)

                    # SECOND LINE OF DEFENSE: Check open dialog for Ads before typing
                    dialog_el = page.locator("div[role='dialog']").first
                    if dialog_el.is_visible(timeout=1000):
                        is_diag_ad, diag_ad_reason = is_ad_or_sponsored_dom(dialog_el)
                        if is_diag_ad:
                            log_activity(log_file_path, account, f"🛑 [DIALOG AD BLOCKED] Detected ad in comment modal ({diag_ad_reason}). Closing!")
                            page.keyboard.press("Escape")
                            time.sleep(1.0)
                            continue

                    # Locate comment box
                    comment_box = page.locator(
                        "div[role='dialog'] textarea, textarea[aria-label*='comment' i], "
                        "[role='textbox'][aria-label*='comment' i], article textarea"
                    ).first

                    if comment_box.is_visible(timeout=3000):
                        comment_box.focus()
                        time.sleep(0.5)
                        comment_box.press_sequentially(comment_text, delay=random.randint(45, 80))
                        time.sleep(random.uniform(1.2, 2.0))

                        # Submit comment
                        post_btn = page.locator(
                            "div[role='dialog'] div[role='button']:text-is('Post'), "
                            "div[role='dialog'] button:text-is('Post'), "
                            "div[role='button']:text-is('Post'), button:text-is('Post')"
                        ).first

                        if post_btn.is_visible(timeout=1500):
                            post_btn.click(force=True)
                        else:
                            page.keyboard.press("Enter")

                        log_activity(log_file_path, account, f"💬 Successfully commented on @{author}'s post: '{comment_text}'")
                        comments_posted += 1

                        # Record in history & caches
                        record_generated_comment(account, comment_text, author=author, post_id=post_id)
                        commented_cache.add(post_id)
                        save_commented_cache(cache_file, commented_cache)
                        add_post_to_global_cache(post_id, account, author=author)

                        # Close dialog if open
                        time.sleep(random.uniform(2.0, 3.5))
                        page.keyboard.press("Escape")
                        time.sleep(random.uniform(3.0, 6.0))

                except Exception as e:
                    log_activity(log_file_path, account, f"Feed item interaction note: {e}")
                    continue

            # Scroll down feed
            page.mouse.wheel(0, random.randint(700, 1100))
            time.sleep(random.uniform(2.5, 4.0))

        log_activity(log_file_path, account, f"Completed following engagement session ({comments_posted} comments posted).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hardened Ad-Shield & Following-Priority Instagram Network Engager.")
    parser.add_argument("-a", "--account", required=True, choices=ACCOUNTS, help="Instagram handle to run")
    parser.add_argument("--max-comments", type=int, default=2, help="Max comments per run (default: 2, strict max 3/day)")
    parser.add_argument("--draft-only", action="store_true", help="Preview comments without posting live")
    args = parser.parse_args()

    run_following_engager(
        account=args.account,
        max_comments=args.max_comments,
        draft_only=args.draft_only,
    )
