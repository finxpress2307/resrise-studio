"""Utility functions for Resrise Studio automation scripts."""
import os
import sys
from pathlib import Path
from typing import Optional, List
import re

from .config import get_settings


def get_project_dir() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parents[2]


def get_scripts_dir() -> Path:
    """Get the scripts directory."""
    return get_project_dir() / "scripts"


def get_chrome_profile_dir(account: str) -> Path:
    """Get Chrome user data directory for an account."""
    local_app_data = os.environ.get(
        "LOCALAPPDATA", r"C:\Users\Default\AppData\Local"
    )
    return Path(local_app_data) / "Google" / "Chrome" / "User Data - Automation" / account


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if needed."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_account(account: str) -> str:
    """Validate and normalize an Instagram account handle."""
    from .config import get_settings

    cleaned = account.strip().lstrip("@").lower()
    settings = get_settings()
    if cleaned not in settings.instagram_accounts:
        raise ValueError(
            f"Unsupported account '{account}'. "
            f"Choose from: {', '.join(settings.instagram_accounts)}"
        )
    return cleaned


def clean_chrome_locks(profile_dir: Path) -> None:
    """Remove Chrome lock files from a profile directory."""
    lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]
    for lock_file in lock_files:
        lock_path = profile_dir / lock_file
        if lock_path.exists():
            try:
                lock_path.unlink()
            except Exception:
                pass


def get_valid_media_paths(paths: List[str]) -> List[str]:
    """Filter media paths to only existing files."""
    return [p for p in paths if p and Path(p).exists()]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage."""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255 - len(ext)] + ext
    return sanitized


def parse_media_paths(raw_paths: str) -> List[str]:
    """Parse media paths from textarea input (one per line)."""
    return [line.strip() for line in raw_paths.splitlines() if line.strip()]


def format_media_paths(paths: List[str]) -> str:
    """Format media paths for textarea display."""
    return "\n".join(paths)


def generate_short_id(length: int = 8) -> str:
    """Generate a short unique ID."""
    import uuid
    return str(uuid.uuid4())[:length]


def normalize_path(path: str) -> str:
    """Normalize a file path for the current platform."""
    return str(Path(path).resolve())


def is_subpath(child: Path, parent: Path) -> bool:
    """Check if child path is within parent directory (prevents path traversal)."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def find_unassigned_media(account: str, queue: list, max_files: int = 10) -> list:
    """Look in draft_media/<account>/ for unassigned images/videos (supports up to 10-slide carousels)."""
    account_media_dir = get_settings().draft_media_dir / account
    account_media_dir.mkdir(parents=True, exist_ok=True)
    used_files = set()
    for item in queue:
        for p in item.get("media_paths", []):
            used_files.add(os.path.normcase(os.path.abspath(p)))
        if item.get("media_path"):
            used_files.add(os.path.normcase(os.path.abspath(item["media_path"])))

    valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov")
    found = []
    for fname in sorted(os.listdir(account_media_dir)):
        if fname.lower().endswith(valid_exts):
            full_path = os.path.abspath(os.path.join(account_media_dir, fname))
            if os.path.normcase(full_path) not in used_files:
                found.append(full_path)
                if len(found) >= max_files:
                    break
    return found


def get_media_list(item: dict) -> list:
    """Get media paths list from item (handles both media_paths list and media_path single)."""
    paths = item.get("media_paths")
    if isinstance(paths, list):
        return [p.strip() for p in paths if p and p.strip()]
    single = item.get("media_path", "").strip()
    return [single] if single else []


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, rate: float, burst: int = 1):
        """
        Args:
            rate: Requests per second (e.g., 0.5 = 1 request per 2 seconds)
            burst: Maximum burst allowance
        """
        import time
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.last_update = time.monotonic()

    def acquire(self, tokens: int = 1, blocking: bool = True) -> bool:
        """
        Acquire tokens from the bucket.

        Returns:
            True if tokens acquired, False if not available and not blocking
        """
        import time

        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        if not blocking:
            return False

        # Wait for tokens
        wait_time = (tokens - self.tokens) / self.rate
        time.sleep(wait_time)
        self.tokens = 0
        self.last_update = time.monotonic()
        return True

    async def aacquire(self, tokens: int = 1) -> None:
        """Async acquire tokens."""
        import asyncio

        while not self.acquire(tokens, blocking=False):
            await asyncio.sleep(0.1)