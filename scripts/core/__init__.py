"""Resrise Studio - Core Shared Modules"""
from .config import Settings, load_settings
from .logging import get_logger, configure_logging
from .utils import get_project_dir, get_chrome_profile_dir, ensure_dir
from .browser import BrowserManager
from .vision import VisionClient, VisionProvider
from .anti_repetition import (
    is_comment_repetitive,
    record_generated_comment,
    get_daily_comment_count,
    is_post_globally_commented,
    add_post_to_global_cache,
)

__all__ = [
    "Settings",
    "load_settings",
    "get_logger",
    "configure_logging",
    "get_project_dir",
    "get_chrome_profile_dir",
    "ensure_dir",
    "BrowserManager",
    "VisionClient",
    "VisionProvider",
    "is_comment_repetitive",
    "record_generated_comment",
    "get_daily_comment_count",
    "is_post_globally_commented",
    "add_post_to_global_cache",
]