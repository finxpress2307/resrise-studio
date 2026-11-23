"""Anti-repetition guards and global cross-account collision prevention."""
import json
import os
import re
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

HISTORY_FILE = os.path.join(PROJECT_DIR, "generated_comments_history.json")
GLOBAL_CACHE_FILE = os.path.join(PROJECT_DIR, "commented_posts_global_cache.json")


def load_comments_history(history_file: str = None) -> list[dict]:
    """Loads rolling history of generated comments."""
    path = history_file or HISTORY_FILE
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []


def save_comments_history(history: list[dict], history_file: str = None) -> None:
    """Saves rolling history of comments, strictly capped at the last 30 entries."""
    path = history_file or HISTORY_FILE
    try:
        trimmed = history[-30:] if len(history) > 30 else history
        with open(path, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def record_generated_comment(
    account: str,
    comment_text: str,
    post_id: str = "",
    history_file: str = None,
) -> None:
    """Records a new generated comment into the rolling 30-comment history."""
    history = load_comments_history(history_file)
    entry = {
        "account": account.lstrip("@").lower(),
        "comment": comment_text.strip(),
        "post_id": post_id,
        "timestamp": datetime.now().isoformat(),
    }
    history.append(entry)
    save_comments_history(history, history_file)


def tokenize_comment_words(text: str) -> set[str]:
    """Tokenize comment into lowercase alphanumeric words, filtering out short punctuation."""
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    words = {w for w in cleaned.split() if len(w) > 2}
    if not words:
        words = set(cleaned.split())
    return words


def compute_word_overlap(text1: str, text2: str) -> float:
    """
    Computes word overlap fraction between two comments relative to the smaller set.
    Returns value between 0.0 and 1.0.
    """
    w1 = tokenize_comment_words(text1)
    w2 = tokenize_comment_words(text2)
    if not w1 or not w2:
        return 0.0
    common = w1.intersection(w2)
    return len(common) / min(len(w1), len(w2))


def is_comment_repetitive(
    candidate_text: str,
    history: list[dict] = None,
    max_overlap: float = 0.50,
    lookback_hours: float = 72.0,
    history_file: str = None,
) -> tuple[bool, str]:
    """
    Rejects any candidate comment that shares more than max_overlap (50%) word overlap
    with any comment used across the studio in the last lookback_hours (72 hours).
    Returns (is_repetitive, reason).
    """
    if history is None:
        history = load_comments_history(history_file)

    now = datetime.now()

    for item in reversed(history):
        past_comment = item.get("comment", "")
        ts_str = item.get("timestamp", "")
        if not past_comment:
            continue

        is_recent = True
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is not None:
                    ts = ts.replace(tzinfo=None)
                if (now - ts) > timedelta(hours=lookback_hours):
                    is_recent = False
            except Exception:
                is_recent = True

        if not is_recent:
            continue

        overlap = compute_word_overlap(candidate_text, past_comment)
        if overlap > max_overlap:
            pct = int(round(overlap * 100))
            return True, f"Shares {pct}% word overlap with comment used in last {int(lookback_hours)}h: '{past_comment}'"

    return False, ""


def get_daily_comment_count(
    account: str,
    history: list[dict] = None,
    history_file: str = None,
    hours: float = 24.0,
) -> int:
    """Returns number of comments posted by this account in the rolling 24-hour window."""
    if history is None:
        history = load_comments_history(history_file)

    clean_acc = account.lstrip("@").lower()
    now = datetime.now()
    count = 0

    for item in history:
        if item.get("account", "").lstrip("@").lower() == clean_acc:
            ts_str = item.get("timestamp", "")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    if ts.tzinfo is not None:
                        ts = ts.replace(tzinfo=None)
                    if (now - ts) <= timedelta(hours=hours):
                        count += 1
                except Exception:
                    count += 1
            else:
                count += 1
    return count


# ---------------- GLOBAL CROSS-ACCOUNT CACHE ----------------


def load_global_cache(cache_file: str = None) -> dict:
    """Loads global cross-account comment cache."""
    path = cache_file or GLOBAL_CACHE_FILE
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                elif isinstance(data, list):
                    return {k: {"account": "unknown"} for k in data}
        except Exception:
            return {}
    return {}


def save_global_cache(data: dict, cache_file: str = None) -> None:
    """Persists global cross-account comment cache."""
    path = cache_file or GLOBAL_CACHE_FILE
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def normalize_post_identifier(post_url_or_id: str) -> str:
    """Extracts canonical shortcode from an Instagram post/reel URL or ID."""
    if not post_url_or_id:
        return ""
    clean = post_url_or_id.split("?")[0].strip("/")
    match = re.search(r"/(?:p|reel)/([A-Za-z0-9_-]+)", post_url_or_id)
    if match:
        return match.group(1)
    if clean.startswith("p/"):
        return clean.split("p/")[1]
    if clean.startswith("reel/"):
        return clean.split("reel/")[1]
    parts = clean.split("/")
    return parts[-1] if parts else clean


def is_post_globally_commented(
    post_id: str,
    cache_file: str = None,
) -> tuple[bool, str]:
    """
    Checks if a post has already been commented on by ANY studio account.
    Returns (is_commented, account_name).
    """
    cache = load_global_cache(cache_file)
    norm = normalize_post_identifier(post_id)
    if not norm:
        return False, ""

    if norm in cache:
        entry = cache[norm]
        acc = entry.get("account", "unknown") if isinstance(entry, dict) else "unknown"
        return True, acc

    if post_id in cache:
        entry = cache[post_id]
        acc = entry.get("account", "unknown") if isinstance(entry, dict) else "unknown"
        return True, acc

    for key, val in cache.items():
        if normalize_post_identifier(key) == norm:
            acc = val.get("account", "unknown") if isinstance(val, dict) else "unknown"
            return True, acc

    return False, ""


def add_post_to_global_cache(
    post_id: str,
    account: str,
    author: str = "",
    comment_text: str = "",
    cache_file: str = None,
) -> None:
    """Registers a newly commented post into the global cross-account cache."""
    cache = load_global_cache(cache_file)
    norm = normalize_post_identifier(post_id)
    entry = {
        "account": account.lstrip("@").lower(),
        "author": author,
        "comment": comment_text,
        "timestamp": datetime.now().isoformat(),
        "original_id": post_id,
    }
    cache[norm] = entry
    save_global_cache(cache, cache_file)
