"""
Resrise Studio - Instagram Comment Replier (Root Wrapper)
Synchronized wrapper pointing to scripts/ig_replier.py for complete Telegram funnel
and affiliate trigger handling across the Resrise Creator Swarm.
"""

from __future__ import annotations

import os
import sys

# Ensure scripts directory is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Re-export all symbols from scripts.ig_replier
from scripts.ig_replier import (
    ACCOUNTS,
    AFFILIATE_KEYWORDS,
    AFFILIATE_KEYWORD_REPLIES,
    TELEGRAM_CHANNELS,
    parse_account,
    check_affiliate_trigger,
    get_affiliate_trigger_details,
    simulate_comment_replies,
    is_already_responded,
    main,
)

if __name__ == "__main__":
    main()
