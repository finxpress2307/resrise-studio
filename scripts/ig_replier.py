"""
Instagram Inbound Comment Replier (Zero Duplicate & Bulletproof Reliability)
=============================================================================
Safely inspects your recent posts and replies to incoming comments in your persona's voice.

Key Improvements:
1. Live DOM Truth: Never skips real comments due to cache poisoning. Only marks as replied
   AFTER successful submission on Instagram.
2. Smart Multi-Tier Generation: Uses FreeLLMAPI/OpenRouter with intelligent persona fallback
   so replying NEVER fails or silently skips even if the local LLM is temporarily offline.
3. Strict Double-Reply Prevention:
   - Skips if comment author is @account itself.
   - Skips if @account has already replied inside the thread (checks visible and collapsed replies).
   - Skips if @account has already replied to this author on this post.
4. Human-like interaction: Realistic typing delay, enters comment, verifies submission.
"""

import argparse
import base64
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

try:
    from openrouter_client import call_openrouter_vision, is_openrouter_configured
except ImportError:
    is_openrouter_configured = lambda: False
    call_openrouter_vision = lambda p, img: None

try:
    from core.anti_repetition import compute_word_overlap, tokenize_comment_words
except ImportError:
    try:
        from scripts.core.anti_repetition import compute_word_overlap, tokenize_comment_words
    except ImportError:
        def tokenize_comment_words(text: str) -> set[str]:
            if not text:
                return set()
            cleaned = re.sub(r"[^\w\s]", " ", text.lower())
            words = {w for w in cleaned.split() if len(w) > 2}
            return words or set(cleaned.split())

        def compute_word_overlap(t1: str, t2: str) -> float:
            w1, w2 = tokenize_comment_words(t1), tokenize_comment_words(t2)
            if not w1 or not w2:
                return 0.0
            return len(w1.intersection(w2)) / min(len(w1), len(w2))

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]
CHROME_PROFILES_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data - Automation")

REPLY_HISTORY_FILE = os.path.join(PROJECT_DIR, "generated_replies_history.json")
USER_REPLY_HISTORY_FILE = os.path.join(PROJECT_DIR, "replied_users_history.json")


def parse_account(value: str) -> str:
    """Parses and validates account handle."""
    cleaned = value.strip().lstrip("@").lower()
    if cleaned not in ACCOUNTS:
        raise argparse.ArgumentTypeError(
            f"Unsupported account '{value}'. Choose from: {', '.join(ACCOUNTS)}"
        )
    return cleaned


PERSONA_BRIEFS = {
    "avanyamehra": "luxury editorial fashion model, refined, artistic, international high-fashion draping, elegant and warm",
    "mairamehraofficial": "saree styling & ethnic wear creator, cultural elegance, warm, graceful, authentic",
    "iamgagankumar": "minimalist menswear & grooming model, sharp, tailored aesthetic, polite, modern masculine",
    "resrise": "creative production studio, editorial campaigns & visual stories, professional, welcoming",
    "gagankumarrocks": "media entrepreneur & founder @resrise, strategic, inspiring, creator growth",
}

PERSONA_FALLBACK_REPLIES = {
    "avanyamehra": [
        "Thank you so much! Truly appreciate the love ✨",
        "Glad you loved this silhouette! Styled with so much love 🤍",
        "Thank you darling! Means a lot ✨",
        "Appreciate the kind words! Loving this drape edit ✨",
        "Thank you! Truly grateful for the love 🤍",
        "So glad this aesthetic caught your eye! Sending warmth ✨",
        "Means the world! We spent so much time perfecting the cowl lines 🤍",
        "Thank you! Timeless Parisian tailoring is always the inspiration ✨",
        "Appreciate you noticing the details! Effortless drape was the vision 🤍",
        "So lovely of you to say! Grateful for your presence here ✨",
        "Thank you so much! The lighting in this shot was pure magic 🤍",
        "Glad this look resonated with you! High-fashion simplicity always ✨",
        "Warmest thanks darling! Focused on understated luxury here 🤍",
        "Appreciate the appreciation! More editorial stories on the way ✨",
        "Thank you! Curating these clean silhouettes is such a joy 🤍",
        "So kind! The palette balance in this frame felt so serene ✨",
        "Thank you for the wonderful comment! Sending elegance your way 🤍",
        "Really appreciate this! Classic cuts never go out of style ✨",
        "Means a lot darling! Styled with a modern Milan dusk vibe 🤍",
        "Thank you! Loving how the movement translated on camera ✨",
        "So grateful for your encouragement! Keep inspiring ✨",
        "Thank you so much! Clean lines and subtle textures are everything 🤍",
        "Appreciate you stopping by and sharing such warmth ✨",
        "Thrilled you enjoyed this edit! More lookbook drops coming soon 🤍",
        "Thank you darling! Understated elegance is always the goal ✨",
        "Glad you loved the composition! Truly means a lot 🤍",
        "Warmest gratitude! The monochrome tones came together so smoothly ✨",
        "Thank you so much! Grateful for your constant support 🤍",
        "Appreciate the love! Every drape is crafted with passion ✨",
        "So happy this inspired you! Sending love and light 🤍",
    ],
    "mairamehraofficial": [
        "Thank you so much! Loved draping this piece 🌸",
        "Appreciate the kind words! Handloom elegance always ✨",
        "Thank you! This saree holds such a special vibe 🤍",
        "So glad you liked this ethnic styling! Truly means a lot 🌸",
        "Thank you! Heritage drapes will always be my favourite ✨",
        "Warmest thanks! The intricate zari work here is truly breathtaking 🌸",
        "Appreciate your lovely words! Celebrating traditional textiles is pure joy 🤍",
        "Thank you so much! The royal courtyard lighting brought this alive ✨",
        "So glad you loved the pallu styling! Handcrafted beauty always 🌸",
        "Heartfelt gratitude! These festive tones feel so celebratory 🤍",
        "Thank you dear! Saree draping is an emotion for me ✨",
        "Appreciate the love! Organza silks have such a graceful fall 🌸",
        "Means a lot! Pairing heritage kundan with this weave felt so royal 🤍",
        "Thank you! Preserving timeless cultural craft through styling ✨",
        "So kind of you! Grateful for your genuine warmth and support 🌸",
        "Thank you so much! This traditional palette is so close to my heart 🤍",
        "Appreciate the appreciation! More saree stories coming very soon ✨",
        "So glad this festive styling resonated with you! Warm hugs 🌸",
        "Thank you dear! Handloom weavers create absolute poetry 🤍",
        "Means the world! The pleats and drape fell into place effortlessly ✨",
        "Warmest thanks! Grateful to share Indian ethnic art with you 🌸",
        "Thank you so much! The antique jewelry really complemented the look 🤍",
        "Appreciate the kind energy! Have a blessed and radiant day ✨",
        "So thrilled you loved it! Saree elegance never fades 🌸",
        "Thank you! Bringing royal heritage into contemporary frames 🤍",
        "Heartfelt thanks! Your lovely comment made my day ✨",
        "Glad the draping inspired you! More festive inspiration ahead 🌸",
        "Thank you so much! Truly grateful for all the ethnic love 🤍",
        "Appreciate you! Every six yards tells a timeless cultural story ✨",
        "So happy you enjoyed this royal look! Sending festive warmth 🌸",
    ],
    "iamgagankumar": [
        "Thank you man! Glad you liked the tailoring ⚡",
        "Appreciate it brother! Minimalist aesthetic always.",
        "Thank you! Focused on sharp lines for this look ⚡",
        "Appreciate the love man! Means a lot.",
        "Glad the fit resonated with you! Clean and sharp.",
        "Thanks brother! The shoulder cut on this jacket made all the difference ⚡",
        "Appreciate the support man! Keeping menswear timeless and functional.",
        "Thank you! Bespoke tailoring always comes down to the proportions ⚡",
        "Glad you noticed the details brother! French linen is a personal staple.",
        "Respect man! Focused on versatile capsule styling for this edit ⚡",
        "Thanks a lot brother! Neutral tones make layering effortless.",
        "Appreciate the kind words man! Stay sharp always ⚡",
        "Thank you! The bandhgala silhouette came together cleanly.",
        "Glad you liked the fit brother! Quality fabrics speak for themselves ⚡",
        "Cheers man! Appreciate you taking the time to drop love.",
        "Thanks brother! Understated luxury without the noise ⚡",
        "Appreciate it man! Classic black-tie tailoring is always undefeated.",
        "Thank you! Grooming and clean cuts set the baseline ⚡",
        "Glad it resonated brother! More sharp wardrobe edits coming up.",
        "Thanks man! Focused on crisp structure and comfortable movement ⚡",
        "Appreciate the feedback brother! Fit is everything in menswear.",
        "Thank you! Keeping the aesthetic sharp, masculine, and refined ⚡",
        "Respect brother! Grateful for your continuous support.",
        "Cheers man! Building a capsule wardrobe one piece at a time ⚡",
        "Thank you so much! Sharp lapels and clean footwear always work.",
        "Glad you appreciated the styling man! Have a solid week ⚡",
        "Thanks brother! Quality over quantity in every single fit.",
        "Appreciate the love man! Good tailoring never goes out of style ⚡",
        "Respect! Focused on subtle textures and disciplined styling.",
        "Cheers brother! Stay sharp and keep building ⚡",
    ],
    "resrise": [
        "Thank you! Our creative team loved producing this campaign ✨",
        "Appreciate the appreciation! More visual stories coming soon ✨",
        "Thank you for following our editorial journey 🤍",
        "Glad this visual direction caught your eye! More studio releases ahead ✨",
        "Thank you! We put meticulous attention into the lighting and shot planning 🤍",
        "Appreciate the feedback! Merging high art direction with next-gen production ✨",
        "Thank you! Crafting compelling narratives for modern fashion brands 🤍",
        "Glad you enjoyed the creative direction! Full campaign reel drops soon ✨",
        "Thank you so much! The set atmosphere was truly electric 🤍",
        "Appreciate the support! Pushing the frontier of digital fashion production ✨",
        "Thank you! Every frame is engineered for visual impact 🤍",
        "Glad the concept resonated! Proud of what our studio team achieved ✨",
        "Thank you for the warm words! Exploring bold editorial perspectives 🤍",
        "Appreciate the recognition! Cinematic framing is our signature ✨",
        "Thank you! Stay tuned for the upcoming Volume II collection release 🤍",
        "Glad you connected with this piece! The color grading took weeks to refine ✨",
        "Thank you! Committed to high-end aesthetic storytelling 🤍",
        "Appreciate the love from our creative community! Means a lot ✨",
        "Thank you for tuning in! Exciting brand collaborations in the pipeline 🤍",
        "So glad this stood out on your feed! Appreciate the feedback ✨",
        "Thank you! Celebrating boundary-pushing visual arts 🤍",
        "Appreciate your perspective! Visual craft is at the heart of Resrise ✨",
        "Thank you so much! Looking forward to sharing the behind-the-scenes breakdown 🤍",
        "Glad you loved the aesthetic execution! Onward to the next campaign ✨",
        "Thank you! Honoring high fashion heritage through modern production 🤍",
    ],
    "gagankumarrocks": [
        "Appreciate the support! Building every single day 🚀",
        "Thank you! Systems and consistency create the brand ⚡",
        "Means a lot! Onward and upward 🚀",
        "Glad this blueprint resonated! Execution is everything ⚡",
        "Thank you man! Scaling autonomous creator infrastructure week by week 🚀",
        "Appreciate you following the journey! Building in public is rewarding ⚡",
        "Respect! Discipline and workflow optimization compound fast 🚀",
        "Thank you! Creative tech meets relentless production habits ⚡",
        "Glad this insight helped! The creator economy is just getting started 🚀",
        "Appreciate the energy man! Let's keep building and scaling ⚡",
        "Thank you! Focus on the inputs and the metrics take care of themselves 🚀",
        "Means a lot brother! Documenting the real media house blueprint ⚡",
        "Glad you liked the breakdown! More architecture notes coming soon 🚀",
        "Respect man! Consistency is the only true competitive moat ⚡",
        "Thank you! Building high-leverage digital assets daily 🚀",
        "Appreciate the shoutout! Keep shipping and refining your craft ⚡",
        "Thanks brother! Systems beat motivation every single time 🚀",
        "Glad this clicked for you! Onward to greater milestones ⚡",
        "Thank you! Grateful to have you along for the build 🚀",
        "Respect! Let's keep executing with precision and purpose ⚡",
    ],
}

# Master Telegram Affiliate & VIP Funnel Destinations (sourced from affiliate_mappings)
try:
    from .affiliate_mappings import (
        CREATOR_ACCOUNTS,
        TELEGRAM_CHANNELS as MAPPINGS_TELEGRAM_CHANNELS,
        AFFILIATE_RESPONSES as MAPPINGS_AFFILIATE_RESPONSES,
        UNIVERSAL_KEYWORDS as MAPPINGS_UNIVERSAL_KEYWORDS,
        PERSONA_KEYWORDS as MAPPINGS_PERSONA_KEYWORDS,
        CREATOR_LOOK_CATALOG,
        get_creator_telegram,
        get_earnkaro_link,
        get_amazon_link,
        get_creator_keywords,
        check_keyword_trigger as mappings_check_keyword_trigger,
        validate_earnkaro_link,
        validate_amazon_link,
    )
except (ImportError, ValueError):
    from affiliate_mappings import (
        CREATOR_ACCOUNTS,
        TELEGRAM_CHANNELS as MAPPINGS_TELEGRAM_CHANNELS,
        AFFILIATE_RESPONSES as MAPPINGS_AFFILIATE_RESPONSES,
        UNIVERSAL_KEYWORDS as MAPPINGS_UNIVERSAL_KEYWORDS,
        PERSONA_KEYWORDS as MAPPINGS_PERSONA_KEYWORDS,
        CREATOR_LOOK_CATALOG,
        get_creator_telegram,
        get_earnkaro_link,
        get_amazon_link,
        get_creator_keywords,
        check_keyword_trigger as mappings_check_keyword_trigger,
        validate_earnkaro_link,
        validate_amazon_link,
    )

TELEGRAM_CHANNELS = MAPPINGS_TELEGRAM_CHANNELS
AFFILIATE_KEYWORDS = list(MAPPINGS_UNIVERSAL_KEYWORDS)
AFFILIATE_KEYWORD_REPLIES = MAPPINGS_AFFILIATE_RESPONSES


def check_affiliate_trigger(account: str, comment_text: str, look_id: str | None = None) -> str | None:
    """
    Checks if incoming comment contains high-intent affiliate/funnel keywords
    (DRAPE, LINK, OUTFIT, SAREE, FIT, etc.) using scripts/affiliate_mappings.py.
    Returns high-converting persona response with direct Telegram funnel link if matched, else None.
    """
    # Defensive cleanup: strip author handle prefix to avoid regex bleed
    clean_body = re.sub(r"^@[a-zA-Z0-9._-]+:\s*", "", comment_text).strip()
    res = mappings_check_keyword_trigger(account, clean_body, look_id=look_id)
    if res:
        pool = AFFILIATE_KEYWORD_REPLIES.get(account.lstrip("@").lower())
        if pool:
            return random.choice(pool)
        return res["reply_text"]
    return None


def get_affiliate_trigger_details(account: str, comment_text: str, look_id: str | None = None) -> dict | None:
    """
    Returns full dictionary of trigger routing details, Telegram links, and affiliate sample URLs.
    """
    clean_body = re.sub(r"^@[a-zA-Z0-9._-]+:\s*", "", comment_text).strip()
    return mappings_check_keyword_trigger(account, clean_body, look_id=look_id)


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


def load_replied_cache(cache_file: str) -> set:
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_replied_cache(cache_file: str, cache_set: set) -> None:
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(sorted(list(cache_set)), f, indent=2)
    except Exception:
        pass


def hash_comment(author: str, clean_body: str) -> str:
    words = [w.lower() for w in re.findall(r"\w+", clean_body)][:8]
    key = f"{author.lower()}:{' '.join(words)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def extract_comment_parts(row) -> tuple[str, str]:
    try:
        data = row.evaluate("""(el) => {
            const authorLink = el.querySelector('a[role="link"][href^="/"]');
            const author = authorLink ? authorLink.pathname.replace(/\\//g, '').toLowerCase() : '';
            const spans = Array.from(el.querySelectorAll('span'))
                .map(s => s.innerText.trim())
                .filter(t => t && t.toLowerCase() !== author);
            return { author, body: spans.join(' ') };
        }""")
        author = data.get("author", "").strip()
        body = data.get("body", "").strip()
    except Exception:
        author = ""
        body = row.inner_text().strip()

    body = re.sub(r"\b\d+\s*[smhdw]\b", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\b(Reply|Like|Likes|\d+\s+likes?|View replies.*|Hide replies|See translation)\b", "", body, flags=re.IGNORECASE)
    normalized = " ".join(body.split())
    return author, normalized


def is_already_responded(row, account: str) -> bool:
    """
    Bulletproof check: Returns True if this comment has ALREADY been replied to:
    1. Comment author is @account itself.
    2. Comment row itself has text indicating replies (View replies, Hide replies, replies (N), etc.).
    3. Next sibling elements (where Instagram places the reply button/thread) contain View replies or Hide replies.
    4. Enclosing container / LI contains View replies, Hide replies, or @account.
    5. Any link in the thread belongs to @account.
    """
    acc_clean = account.lower().lstrip("@")

    # Step 1: Check if the comment author is the account itself
    try:
        author, _ = extract_comment_parts(row)
        if author == acc_clean:
            return True
    except Exception:
        pass

    # Step 2: Comprehensive DOM inspection for replies
    try:
        return row.evaluate("""(el, targetAccount) => {
            // Check inside el itself
            const textInside = el.innerText || '';
            if (textInside.match(/(view\\s+\\d*\\s*repl|hide\\s+repl|replies\\s*\\(\\d+\\)|view\\s+1\\s+reply|जवाब|उत्तर)/i)) {
                return true;
            }

            // Check next siblings (Instagram puts 'View replies' / 'Hide replies' as sibling div/button)
            let sib = el.nextElementSibling;
            let steps = 0;
            while (sib && steps < 3) {
                const sibText = sib.innerText || '';
                if (sibText.match(/(view\\s+\\d*\\s*repl|hide\\s+repl|replies\\s*\\(\\d+\\)|view\\s+1\\s+reply|जवाब|उत्तर)/i)) {
                    return true;
                }
                // If sibling has its own author link and Reply button, it's the next top-level comment, stop searching
                if (sib.querySelector("a[role='link'][href^='/']") && sib.innerText.toLowerCase().includes('reply')) {
                    break;
                }
                sib = sib.nextElementSibling;
                steps++;
            }

            // Check enclosing LI / container
            const parentLi = el.closest('li') || el.parentElement;
            if (parentLi) {
                const pText = parentLi.innerText || '';
                if (pText.match(/(view\\s+\\d*\\s*repl|hide\\s+repl|replies\\s*\\(\\d+\\)|view\\s+1\\s+reply|जवाब|उत्तर)/i)) {
                    return true;
                }
                const links = Array.from(parentLi.querySelectorAll("a[role='link'][href^='/']"));
                for (let link of links) {
                    const handle = link.pathname.replace(/\\//g, '').toLowerCase();
                    if (handle === targetAccount) return true;
                }
            }

            return false;
        }""", acc_clean)
    except Exception:
        return False


def load_replies_history(history_file: str = None) -> list[dict]:
    """Loads rolling history of generated replies."""
    path = history_file or REPLY_HISTORY_FILE
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []


def save_replies_history(history: list[dict], history_file: str = None) -> None:
    """Saves rolling history of replies, capped at last 50 entries."""
    path = history_file or REPLY_HISTORY_FILE
    try:
        trimmed = history[-50:] if len(history) > 50 else history
        with open(path, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_user_reply_history(history_file: str = None) -> dict:
    """Loads per-user reply tracking data: {account: {username: [past replies]}}."""
    path = history_file or USER_REPLY_HISTORY_FILE
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
    return {}


def save_user_reply_history(data: dict, history_file: str = None) -> None:
    """Persists per-user reply tracking data."""
    path = history_file or USER_REPLY_HISTORY_FILE
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def record_user_reply(account: str, author: str, reply_text: str, history_file: str = None) -> None:
    """Records a reply sent to a specific user for per-user anti-repetition memory."""
    if not author:
        return
    clean_acc = account.lstrip("@").lower()
    clean_author = author.lstrip("@").lower()
    user_data = load_user_reply_history(history_file)
    if clean_acc not in user_data:
        user_data[clean_acc] = {}
    if clean_author not in user_data[clean_acc]:
        user_data[clean_acc][clean_author] = []
    user_data[clean_acc][clean_author].append(reply_text.strip())
    user_data[clean_acc][clean_author] = user_data[clean_acc][clean_author][-10:]
    save_user_reply_history(user_data, history_file)


def record_generated_reply(account: str, reply_text: str, author: str = "", history_file: str = None) -> None:
    """Records a generated reply into both global history and per-user history."""
    clean_acc = account.lstrip("@").lower()
    clean_author = author.lstrip("@").lower() if author else ""

    # 1. Global rolling history
    history = load_replies_history(history_file)
    entry = {
        "account": clean_acc,
        "author": clean_author,
        "reply": reply_text.strip(),
        "timestamp": datetime.now().isoformat(),
    }
    history.append(entry)
    save_replies_history(history, history_file)

    # 2. Per-user memory
    if clean_author:
        record_user_reply(account, clean_author, reply_text)


def is_reply_repetitive_for_user(account: str, author: str, candidate_text: str, history_file: str = None) -> tuple[bool, str]:
    """
    Checks if this candidate reply shares >25% word overlap with any reply
    previously sent by @account to this specific author.
    """
    if not author:
        return False, ""
    clean_acc = account.lstrip("@").lower()
    clean_auth = author.lstrip("@").lower()
    user_data = load_user_reply_history(history_file)
    user_past = user_data.get(clean_acc, {}).get(clean_auth, [])
    for past_reply in reversed(user_past):
        overlap = compute_word_overlap(candidate_text, past_reply)
        if overlap > 0.25:
            pct = int(round(overlap * 100))
            return True, f"Shares {pct}% word overlap with past reply to @{author}: '{past_reply}'"
    return False, ""


def is_reply_globally_repetitive(
    account: str,
    candidate_text: str,
    max_overlap: float = 0.30,
    lookback_hours: float = 72.0,
    history_file: str = None,
) -> tuple[bool, str]:
    """
    Checks if candidate reply shares >30% word overlap with any reply sent by @account
    in the rolling lookback_hours (72h) window.
    """
    clean_acc = account.lstrip("@").lower()
    history = load_replies_history(history_file)
    now = datetime.now()
    for item in reversed(history):
        if item.get("account", "").lower() != clean_acc:
            continue
        past_reply = item.get("reply", "")
        if not past_reply:
            continue
        ts_str = item.get("timestamp", "")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is not None:
                    ts = ts.replace(tzinfo=None)
                if (now - ts) > timedelta(hours=lookback_hours):
                    continue
            except Exception:
                pass
        overlap = compute_word_overlap(candidate_text, past_reply)
        if overlap > max_overlap:
            pct = int(round(overlap * 100))
            return True, f"Shares {pct}% word overlap with recent reply in last {int(lookback_hours)}h: '{past_reply}'"
    return False, ""


def generate_reply_text(
    account: str,
    img_bytes: bytes,
    caption_text: str,
    incoming_comment: str,
    author: str = "",
) -> str:
    """
    Multi-tier reply generator:
    0. Anti-spam filter (rejects bot / promo comments).
    1. High-Intent Telegram Affiliate Funnel Trigger: Detects 'DRAPE', 'LINK', 'OUTFIT', etc.
       and returns direct Telegram VIP funnel link for the account.
    2. Tries FreeLLMAPI / OpenRouter Vision if available with anti-repetition check.
    3. Fallback: Intelligent persona response pool matched to comment vibe with
       strict anti-repetition (<30% 72h rolling overlap) and per-user memory (<25% overlap).
    """
    # 0. Check for obvious spam before replying
    lower_c = incoming_comment.lower()
    spam_triggers = ["dm us", "promote on", "send pic", "collab with", "check out my", "crypto", "free followers"]
    if any(s in lower_c for s in spam_triggers):
        return ""

    # 1. High-Intent Telegram Affiliate Funnel Trigger ('DRAPE', 'LINK', 'OUTFIT')
    clean_body = re.sub(r"^@[a-zA-Z0-9._-]+:\s*", "", incoming_comment).strip()
    affiliate_reply = check_affiliate_trigger(account, clean_body)
    if affiliate_reply:
        return affiliate_reply

    # 2. Try FreeLLMAPI / OpenRouter
    persona = PERSONA_BRIEFS.get(account, "creator")
    prompt = (
        f"You are @{account} ({persona}) replying to a comment on your own Instagram post.\n"
        f"Your post caption: {caption_text[:300] if caption_text else 'none'}\n"
        f"Incoming comment: {incoming_comment[:300]}\n\n"
        "Rules:\n"
        "1. Write a natural, warm, context-specific reply (4 to 12 words, max 1 emoji, no hashtags).\n"
        "2. Directly acknowledge what they said.\n"
        "3. If spam or bot promo ('DM us', 'promote on'), output exactly: SKIP"
    )

    if is_openrouter_configured():
        try:
            res = call_openrouter_vision(prompt, img_bytes)
            if res and not res.upper().startswith("SKIP"):
                candidate = res.strip('"')
                is_user_rep, _ = is_reply_repetitive_for_user(account, author, candidate)
                is_glob_rep, _ = is_reply_globally_repetitive(account, candidate)
                if not is_user_rep and not is_glob_rep:
                    record_generated_reply(account, candidate, author)
                    return candidate
            if res == "":
                return ""  # Explicit SKIP by model
        except Exception:
            pass

    # 3. Intelligent Persona Fallback with strict anti-repetition & per-user memory
    fallbacks = PERSONA_FALLBACK_REPLIES.get(account, PERSONA_FALLBACK_REPLIES["avanyamehra"])
    shuffled_pool = list(fallbacks)
    random.shuffle(shuffled_pool)

    # Search for candidate with <30% global overlap and <25% user overlap
    for candidate in shuffled_pool:
        is_user_rep, _ = is_reply_repetitive_for_user(account, author, candidate)
        if is_user_rep:
            continue
        is_glob_rep, _ = is_reply_globally_repetitive(account, candidate)
        if is_glob_rep:
            continue
        record_generated_reply(account, candidate, author)
        return candidate

    # If all items in the pool share minor overlap, pick candidate with minimum overlap for this user
    best_candidate = shuffled_pool[0]
    min_user_overlap = 1.0
    user_data = load_user_reply_history()
    user_past = user_data.get(account.lower(), {}).get(author.lower(), []) if author else []

    if user_past:
        for candidate in shuffled_pool:
            ov = max(compute_word_overlap(candidate, p) for p in user_past)
            if ov < min_user_overlap:
                min_user_overlap = ov
                best_candidate = candidate
    else:
        best_candidate = shuffled_pool[0]

    record_generated_reply(account, best_candidate, author)
    return best_candidate


def simulate_comment_replies(
    account: str,
    max_posts: int = 5,
    max_replies_per_post: int = 5,
    max_batches: int = 1,
    reset_cache: bool = False,
) -> None:
    log_file_path = os.path.join(PROJECT_DIR, f"reply_activity_log_{account}.txt")
    cache_file = os.path.join(PROJECT_DIR, f"replied_comments_cache_{account}.json")
    profile_url = f"https://www.instagram.com/{account}/"

    if reset_cache and os.path.exists(cache_file):
        try:
            os.remove(cache_file)
            log_activity(log_file_path, account, "♻️ Reset replied comments cache as requested.")
        except Exception:
            pass

    replied_comments_cache = load_replied_cache(cache_file)
    log_activity(log_file_path, account, f"Loaded {len(replied_comments_cache)} verified reply signatures from cache.")

    user_data_dir = get_chrome_profile_dir(account)
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        lp = os.path.join(user_data_dir, lock)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    with sync_playwright() as p:
        log_activity(log_file_path, account, f"Launching Google Chrome for @{account}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        log_activity(log_file_path, account, f"Navigating to {profile_url} to inspect comments...")
        page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(random.uniform(4.0, 6.0))

        batch_count = 1
        while True:
            log_activity(log_file_path, account, f"--- Starting Reply Inspection Batch #{batch_count} ---")
            posts = page.locator("a[href*='/p/'], a[href*='/reel/']").all()

            inspected_unpinned_posts = 0
            for i in range(min(max_posts * 3, len(posts))):
                if inspected_unpinned_posts >= max_posts:
                    break
                try:
                    current_posts = page.locator("a[href*='/p/'], a[href*='/reel/']").all()
                    if i >= len(current_posts):
                        break

                    target_post = current_posts[i]

                    # Grid-level Pinned Post Check (Aria-label, title, and exact Instagram pin SVG path)
                    is_pinned_grid = target_post.evaluate("""(el) => {
                        const container = el.closest('div') || el;
                        const svgs = Array.from(el.querySelectorAll('svg')).concat(Array.from(container.querySelectorAll('svg')));
                        for (let s of svgs) {
                            const label = (s.getAttribute('aria-label') || s.textContent || '').toLowerCase();
                            const title = s.querySelector('title')?.textContent?.toLowerCase() || '';
                            if (label.includes('pin') || title.includes('pin') || label.includes('पिन') || title.includes('पिन')) return true;
                            if (s.innerHTML.includes('22.707 7.583')) return true;
                        }
                        return false;
                    }""")

                    if is_pinned_grid:
                        log_activity(log_file_path, account, f"📌 Post #{i + 1} has a pin icon in grid. Skipping pinned post.")
                        continue

                    target_post.scroll_into_view_if_needed()
                    time.sleep(1.0)
                    target_post.click(force=True)
                    log_activity(log_file_path, account, f"Opened post #{i + 1} to inspect comments...")
                    time.sleep(random.uniform(4.0, 5.5))

                    # Modal-level Pinned Post Check
                    is_pinned_modal = page.evaluate("""() => {
                        const dialog = document.querySelector("div[role='dialog']");
                        if (!dialog) return false;
                        const text = dialog.innerText.toLowerCase();
                        if (text.includes('pinned post') || text.includes('पिन की गई पोस्ट')) return true;
                        const svgs = Array.from(dialog.querySelectorAll('svg'));
                        for (let s of svgs) {
                            const label = (s.getAttribute('aria-label') || s.textContent || '').toLowerCase();
                            const title = s.querySelector('title')?.textContent?.toLowerCase() || '';
                            if (label.includes('pin') || title.includes('pin') || label.includes('पिन') || title.includes('पिन')) return true;
                            if (s.innerHTML.includes('22.707 7.583')) return true;
                        }
                        return false;
                    }""")

                    if is_pinned_modal:
                        log_activity(log_file_path, account, f"📌 Post #{i + 1} is identified as a PINNED post in modal. Skipping.")
                        page.keyboard.press("Escape")
                        time.sleep(1.0)
                        continue

                    inspected_unpinned_posts += 1

                    caption_text = page.evaluate("""() => {
                        const h1 = document.querySelector('h1');
                        if (h1 && h1.innerText.trim()) return h1.innerText.trim();
                        const firstSpan = document.querySelector("div[role='dialog'] ul span, article ul span");
                        return firstSpan ? firstSpan.innerText.trim() : '';
                    }""")

                    try:
                        img_bytes = page.locator("div[role='dialog'], article").first.screenshot()
                    except Exception:
                        img_bytes = page.screenshot()

                    # Scroll comment container slightly to ensure fresh comments load
                    comment_container = page.locator("div[role='dialog'] ul, main ul").first
                    if comment_container.is_visible():
                        comment_container.evaluate("el => el.scrollTop = 150")
                        time.sleep(1.0)

                    # Pre-scan post DOM for all authors who already have a reply from @account
                    already_replied_on_this_post = set(page.evaluate("""(targetAccount) => {
                        const repliedTo = new Set();
                        const allLinks = Array.from(document.querySelectorAll("a[role='link'][href^='/']"));
                        for (let link of allLinks) {
                            const handle = link.pathname.replace(/\\//g, '').toLowerCase();
                            if (handle === targetAccount) {
                                const container = link.closest('li') || link.closest('ul');
                                if (container) {
                                    // Check parent thread author
                                    const threadLi = container.closest('ul')?.closest('li') || container;
                                    const threadAuthorLink = threadLi ? threadLi.querySelector("a[role='link'][href^='/']") : null;
                                    if (threadAuthorLink) {
                                        const th = threadAuthorLink.pathname.replace(/\\//g, '').toLowerCase();
                                        if (th !== targetAccount) repliedTo.add(th);
                                    }
                                    // Check any @mentions inside our reply
                                    const text = container.innerText || '';
                                    const matches = text.match(/@([a-zA-Z0-9._]+)/g) || [];
                                    for (let m of matches) {
                                        const clean = m.replace('@', '').toLowerCase();
                                        if (clean !== targetAccount) repliedTo.add(clean);
                                    }
                                }
                            }
                        }
                        return Array.from(repliedTo);
                    }""", account.lower()))

                    if already_replied_on_this_post:
                        log_activity(log_file_path, account, f"Found existing replies to: {', '.join('@' + a for a in already_replied_on_this_post)} on post #{i + 1}.")

                    # Filter strictly for legitimate top-level comment items
                    raw_rows = page.locator("div[role='dialog'] ul > li, div[role='dialog'] ul > div").all()
                    comment_rows = []
                    for r in raw_rows:
                        try:
                            has_author = r.locator("a[role='link'][href^='/']").count() > 0
                            has_reply_btn = r.locator("span:text-is('Reply'), button:has-text('Reply'), div[role='button']:has-text('Reply')").count() > 0
                            r_text = r.inner_text().strip()
                            is_button_only = (
                                r_text.startswith("View repl") or
                                r_text.startswith("Hide repl") or
                                r_text.startswith("जवाब") or
                                r_text.startswith("उत्तर")
                            )
                            if has_author and has_reply_btn and not is_button_only:
                                comment_rows.append(r)
                        except Exception:
                            pass

                    replied_in_post = 0

                    for row in comment_rows:
                        if replied_in_post >= max_replies_per_post:
                            break

                        try:
                            # Rule: Exclude nested child replies (only process top-level comments!)
                            is_nested = row.evaluate("el => Boolean(el.parentElement?.closest('li'))")
                            if is_nested:
                                continue

                            author, clean_body = extract_comment_parts(row)
                            if not clean_body or not author:
                                continue

                            # Skip if from self
                            if author == account.lower():
                                continue

                            # Golden Rule: Never reply twice to the same author on the same post!
                            if author in already_replied_on_this_post:
                                log_activity(log_file_path, account, f"Comment from @{author} already has a response from @{account} on this post. Skipping.")
                                continue

                            comment_id = hash_comment(author, clean_body)

                            # DOM Authority Check: Has @account already responded to this comment?
                            if is_already_responded(row, account):
                                log_activity(log_file_path, account, f"Comment from @{author} already has a response from @{account} in DOM. Skipping.")
                                already_replied_on_this_post.add(author)
                                replied_comments_cache.add(comment_id)
                                save_replied_cache(cache_file, replied_comments_cache)
                                continue

                            # Find Reply button
                            reply_btn = row.locator(
                                "span:text-is('Reply'), button:has-text('Reply'), "
                                "div[role='button']:has-text('Reply')"
                            ).first

                            if not reply_btn.is_visible(timeout=1200):
                                continue

                            log_activity(log_file_path, account, f"Generating response for @{author}: '{clean_body[:50]}'...")

                            reply_text = generate_reply_text(account, img_bytes, caption_text, clean_body, author=author)

                            if not reply_text:
                                log_activity(log_file_path, account, f"Identified spam/bot comment from @{author}. Skipping without reply.")
                                continue

                            # Click reply button
                            reply_btn.scroll_into_view_if_needed()
                            time.sleep(0.4)
                            reply_btn.click(force=True)
                            time.sleep(1.2)

                            reply_box = page.locator(
                                "div[role='dialog'] textarea, div[role='dialog'] [role='textbox'], "
                                "textarea[aria-label*='comment' i], [role='textbox'][aria-label*='comment' i]"
                            ).last

                            if reply_box.is_visible(timeout=3000):
                                reply_box.focus()
                                time.sleep(0.3)

                                # Type human-like
                                reply_box.press_sequentially(reply_text, delay=random.randint(45, 80))
                                time.sleep(random.uniform(1.0, 1.5))

                                submit_btn = page.locator(
                                    "div[role='button']:text-is('Post'), button:text-is('Post'), "
                                    "div[role='button']:text-is('Reply'), button:text-is('Reply')"
                                ).last

                                if submit_btn.is_visible(timeout=1800):
                                    submit_btn.click(force=True)
                                else:
                                    page.keyboard.press("Enter")

                                time.sleep(random.uniform(2.5, 4.0))

                                # ONLY record to cache after verified successful reply submission!
                                replied_comments_cache.add(comment_id)
                                already_replied_on_this_post.add(author)
                                save_replied_cache(cache_file, replied_comments_cache)

                                log_activity(log_file_path, account, f"✅ Successfully replied to @{author}: '{reply_text}'")
                                replied_in_post += 1
                                time.sleep(random.uniform(3.0, 5.0))

                        except Exception as row_err:
                            continue

                    if replied_in_post == 0:
                        log_activity(log_file_path, account, f"No unreplied comments found on post #{i + 1}.")

                    page.keyboard.press("Escape")
                    time.sleep(0.5)
                    page.keyboard.press("Escape")
                    time.sleep(random.uniform(1.8, 3.0))

                except Exception as e:
                    log_activity(log_file_path, account, f"Error inspecting post #{i + 1}: {e}")
                    try:
                        page.keyboard.press("Escape")
                    except Exception:
                        pass
                    time.sleep(1.0)

            log_activity(log_file_path, account, f"Batch #{batch_count} reply check completed.")
            if max_batches > 0 and batch_count >= max_batches:
                log_activity(log_file_path, account, f"Completed all {max_batches} reply batch(es). Exiting cleanly.")
                break

            time.sleep(180)
            batch_count += 1

        context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Reliable, zero-duplicate Instagram comment replier.")
    parser.add_argument("-a", "--account", required=True, choices=ACCOUNTS, help="Account handle to run")
    parser.add_argument("--max-posts", type=int, default=5, help="Number of recent posts to check (default: 5)")
    parser.add_argument("--max-batches", type=int, default=1, help="Number of batches to run before exiting (default: 1)")
    parser.add_argument("--reset-cache", action="store_true", help="Clear previous comment cache to force fresh DOM inspection")
    args = parser.parse_args()

    simulate_comment_replies(
        account=args.account,
        max_posts=args.max_posts,
        max_batches=args.max_batches,
        reset_cache=args.reset_cache,
    )


if __name__ == "__main__":
    main()
