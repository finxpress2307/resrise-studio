"""
Instagram Feed Browsing & Following Engager (Wrapper)
=====================================================
Redirects to the hardened ig_network_engager.py to guarantee:
1. Following Priority (skips strangers, ads, suggested).
2. Zero duplicate comments (checks DOM + persistent local cache + global cross-account cache).
3. Anti-repetition guards on comment generation (<= 50% word overlap in last 72 hours).
4. Daily comment limit (max 2-3 per day).
"""

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "scripts") if os.path.isdir(os.path.join(SCRIPT_DIR, "scripts")) else SCRIPT_DIR
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from ig_network_engager import ACCOUNTS, run_following_engager, generate_peer_comment

try:
    from openrouter_client import is_openrouter_configured, call_openrouter_vision
except ImportError:
    is_openrouter_configured = lambda: False
    call_openrouter_vision = lambda p, img: None


class VisionCommentAgent:
    """Vision-based comment generator using FreeLLMAPI/OpenRouter with persona fallbacks."""

    @staticmethod
    def generate_comment(
        account: str,
        image_bytes: bytes,
        caption_text: str = "",
        creator_handle: str = "",
    ) -> str:
        return generate_peer_comment(account, image_bytes, caption_text)


def simulate_human_browsing(
    account: str,
    draft_only: bool = False,
    max_batches: int = 1,
    batch_size: int = 3,
    cooldown: int = 10,
    **kwargs,
) -> None:
    """Wrapper mapping to the hardened Following-Priority network engager."""
    run_following_engager(
        account=account,
        max_comments=min(batch_size, 3),
        draft_only=draft_only,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vision-aware Instagram feed browsing & followed engagement.")
    parser.add_argument("-a", "--account", required=True, choices=ACCOUNTS, help="Instagram handle to run")
    parser.add_argument("--max-comments", type=int, default=3, help="Max comments per run (default: 3)")
    parser.add_argument("--draft-only", action="store_true", help="Preview comments without posting live")
    parser.add_argument("--live-post", action="store_true", help="Enable live posting (default: True)")
    args = parser.parse_args()

    is_draft = args.draft_only

    run_following_engager(
        account=args.account,
        max_comments=args.max_comments,
        draft_only=is_draft,
    )
