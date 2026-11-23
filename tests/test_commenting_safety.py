"""Tests for Instagram commenting safety, anti-bot overhaul, and cross-account collision prevention."""
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import pytest

from scripts.core.anti_repetition import (
    load_comments_history,
    save_comments_history,
    record_generated_comment,
    compute_word_overlap,
    tokenize_comment_words,
    is_comment_repetitive,
    get_daily_comment_count,
    load_global_cache,
    save_global_cache,
    normalize_post_identifier,
    is_post_globally_commented,
    add_post_to_global_cache,
)
from scripts.ig_network_engager import (
    is_post_from_followed_account,
    has_user_already_commented,
    generate_peer_comment,
    ACCOUNTS,
)


class TestFollowingOnlyValidation:
    """Tests strict followed account validation and ad/sponsored filtering."""

    def test_followed_clean_post(self):
        class MockArticle:
            def evaluate(self, script, *args):
                return {"author": "fashion_creator", "hasFollowBtn": False, "isSponsored": False}

        is_followed, author = is_post_from_followed_account(MockArticle())
        assert is_followed is True
        assert author == "fashion_creator"

    @pytest.mark.parametrize(
        "ad_text",
        [
            "Sponsored post by luxury brand",
            "Suggested for you based on your activity",
            "Promoted content",
            "Special ad discount",
            "Paid partnership with fashionbrand",
            "प्रायोजित सामग्री",
            "आपके लिए सुझाव",
        ],
    )
    def test_sponsored_and_ad_detection(self, ad_text):
        class MockAdArticle:
            def evaluate(self, script, *args):
                return {"author": "some_brand", "hasFollowBtn": False, "isSponsored": True, "text": ad_text}

        is_followed, _ = is_post_from_followed_account(MockAdArticle())
        assert is_followed is False

    def test_stranger_follow_button_rejection(self):
        class MockStrangerArticle:
            def evaluate(self, script, *args):
                return {"author": "stranger_account", "hasFollowBtn": True, "isSponsored": False}

        is_followed, author = is_post_from_followed_account(MockStrangerArticle())
        assert is_followed is False
        assert author == "stranger_account"

    def test_unknown_or_empty_author_rejection(self):
        for bad_author in ["unknown", "UNKNOWN", "", "none", "null"]:
            class MockInvalidArticle:
                def evaluate(self, script, *args, bad=bad_author):
                    return {"author": bad, "hasFollowBtn": False, "isSponsored": False}

            is_followed, author = is_post_from_followed_account(MockInvalidArticle())
            assert is_followed is False
            assert author == ""


class TestGlobalCrossAccountCache:
    """Verifies that no two studio accounts can EVER comment on the same post."""

    def test_normalization_of_post_identifiers(self):
        assert normalize_post_identifier("https://www.instagram.com/p/Df7uly1owSH/") == "Df7uly1owSH"
        assert normalize_post_identifier("https://www.instagram.com/reel/Df7uly1owSH/?igsh=123") == "Df7uly1owSH"
        assert normalize_post_identifier("p/Df7uly1owSH") == "Df7uly1owSH"
        assert normalize_post_identifier("reel/Df7uly1owSH") == "Df7uly1owSH"
        assert normalize_post_identifier("Df7uly1owSH") == "Df7uly1owSH"

    def test_cross_account_collision_prevention(self, tmp_path):
        cache_file = str(tmp_path / "global_cache.json")
        save_global_cache({}, cache_file)

        # 1. Post is initially unseen
        post_url = "https://www.instagram.com/p/Df7uly1owSH/"
        is_commented, acc = is_post_globally_commented(post_url, cache_file)
        assert is_commented is False

        # 2. @avanyamehra comments on it
        add_post_to_global_cache(post_url, "avanyamehra", author="fashion_creator", cache_file=cache_file)

        # 3. @mairamehraofficial checks the exact same post
        is_commented_maira, acc_maira = is_post_globally_commented(post_url, cache_file)
        assert is_commented_maira is True
        assert acc_maira == "avanyamehra"

        # 4. @resrise checks using shortcode format
        is_commented_resrise, acc_resrise = is_post_globally_commented("Df7uly1owSH", cache_file)
        assert is_commented_resrise is True
        assert acc_resrise == "avanyamehra"

        # 5. A completely different post is not blocked
        is_diff, _ = is_post_globally_commented("https://www.instagram.com/p/BrandNewPost123/", cache_file)
        assert is_diff is False


class TestAntiRepetitionGuards:
    """Verifies rolling comment history, >50% overlap rejection, and daily limit."""

    def test_word_overlap_computation(self):
        # >50% overlap (repetitive cliches)
        c1 = "Clean lines and great composition as always!"
        c2 = "Clean lines and sharp styling as always!"
        assert compute_word_overlap(c1, c2) > 0.50

        # Distinct comments (<50% overlap)
        c3 = "Brilliant lighting and creative direction on this frame ✨"
        c4 = "Sharp tailoring on this one! Clean silhouette ⚡"
        assert compute_word_overlap(c3, c4) < 0.50

    def test_rolling_history_max_30_enforcement(self, tmp_path):
        history_file = str(tmp_path / "comments_history.json")

        # Record 45 comments
        for i in range(45):
            record_generated_comment(
                account="avanyamehra",
                comment_text=f"Unique comment number {i} with distinct words ✨",
                post_id=f"post_{i}",
                history_file=history_file,
            )

        history = load_comments_history(history_file)
        assert len(history) == 30
        assert history[-1]["post_id"] == "post_44"

    def test_repetitive_comment_rejection_within_72h(self, tmp_path):
        history_file = str(tmp_path / "comments_history.json")

        base_comment = "Such a stunning silhouette! Loving the movement in this ✨"
        record_generated_comment(
            account="avanyamehra",
            comment_text=base_comment,
            post_id="post_1",
            history_file=history_file,
        )

        # High-overlap variation (>50% word overlap)
        repetitive_candidate = "Such a stunning silhouette! Loving the movement here ✨"
        is_rep, reason = is_comment_repetitive(
            repetitive_candidate,
            history_file=history_file,
            max_overlap=0.50,
            lookback_hours=72.0,
        )
        assert is_rep is True
        assert "Shares" in reason

        # Fresh non-overlapping candidate
        fresh_candidate = "Exquisite handloom textile and rich golden tones 🌸"
        is_rep_fresh, _ = is_comment_repetitive(
            fresh_candidate,
            history_file=history_file,
            max_overlap=0.50,
            lookback_hours=72.0,
        )
        assert is_rep_fresh is False

    def test_comments_older_than_72h_not_blocking(self, tmp_path):
        history_file = str(tmp_path / "comments_history.json")

        old_timestamp = (datetime.now() - timedelta(hours=75)).isoformat()
        old_history = [
            {
                "account": "avanyamehra",
                "comment": "Timeless elegance and graceful framing ✨",
                "timestamp": old_timestamp,
                "post_id": "old_post",
            }
        ]
        save_comments_history(old_history, history_file)

        # Same candidate is now accepted because older than 72 hours
        candidate = "Timeless elegance and graceful framing ✨"
        is_rep, _ = is_comment_repetitive(
            candidate,
            history_file=history_file,
            max_overlap=0.50,
            lookback_hours=72.0,
        )
        assert is_rep is False

    def test_daily_comment_limit_per_account(self, tmp_path):
        history_file = str(tmp_path / "comments_history.json")

        # 3 comments today for @avanyamehra
        for i in range(3):
            record_generated_comment(
                account="avanyamehra",
                comment_text=f"Distinct comment {i} by Avanya",
                post_id=f"post_{i}",
                history_file=history_file,
            )

        # 1 comment today for @mairamehraofficial
        record_generated_comment(
            account="mairamehraofficial",
            comment_text="Distinct comment by Maira",
            post_id="post_maira",
            history_file=history_file,
        )

        assert get_daily_comment_count("avanyamehra", history_file=history_file) == 3
        assert get_daily_comment_count("mairamehraofficial", history_file=history_file) == 1
        assert get_daily_comment_count("iamgagankumar", history_file=history_file) == 0


class TestRunAccountIntegration:
    """Verifies run_account.py uses the hardened following engager."""

    def test_run_account_uses_following_engager(self):
        from scripts import run_account
        assert hasattr(run_account, "run_following_engager")


class TestReplierAntiRepetitionAndUserMemory:
    """Verifies ig_replier per-user memory, >30% global overlap rejection, and expanded template pools."""

    def test_expanded_persona_fallback_pools(self):
        from scripts.ig_replier import PERSONA_FALLBACK_REPLIES, ACCOUNTS
        for acc in ACCOUNTS:
            assert acc in PERSONA_FALLBACK_REPLIES
            pool = PERSONA_FALLBACK_REPLIES[acc]
            assert len(pool) >= 20, f"Account {acc} fallback pool has only {len(pool)} items"

    def test_per_user_reply_repetition_guard(self, tmp_path, monkeypatch):
        import scripts.ig_replier as replier
        user_history_file = str(tmp_path / "user_replies.json")
        monkeypatch.setattr(replier, "USER_REPLY_HISTORY_FILE", user_history_file)

        account = "avanyamehra"
        author = "ajazkhan78696"
        first_reply = "Thank you darling! Means a lot ✨"

        replier.record_user_reply(account, author, first_reply, history_file=user_history_file)

        # Exact repeat must be blocked
        is_rep, reason = replier.is_reply_repetitive_for_user(account, author, first_reply)
        assert is_rep is True
        assert "Shares 100% word overlap" in reason

        # High overlap variation must be blocked
        rep_candidate = "Thank you darling! Means the world ✨"
        is_rep_var, _ = replier.is_reply_repetitive_for_user(account, author, rep_candidate)
        assert is_rep_var is True

        # Completely distinct reply to same user must be allowed
        distinct_reply = "So lovely of you to say! Grateful for your presence here ✨"
        is_distinct, _ = replier.is_reply_repetitive_for_user(account, author, distinct_reply)
        assert is_distinct is False

    def test_global_reply_repetition_guard(self, tmp_path, monkeypatch):
        import scripts.ig_replier as replier
        global_history_file = str(tmp_path / "global_replies.json")
        monkeypatch.setattr(replier, "REPLY_HISTORY_FILE", global_history_file)

        account = "mairamehraofficial"
        base_reply = "Warmest thanks! The intricate zari work here is truly breathtaking 🌸"
        replier.record_generated_reply(account, base_reply, "user1", history_file=global_history_file)

        # Repetitive candidate (>30% overlap)
        rep_candidate = "Warmest thanks! The intricate zari work is breathtaking 🌸"
        is_rep, _ = replier.is_reply_globally_repetitive(account, rep_candidate, history_file=global_history_file)
        assert is_rep is True

        # Fresh candidate
        fresh_candidate = "Appreciate your lovely words! Celebrating traditional textiles is pure joy 🤍"
        is_fresh, _ = replier.is_reply_globally_repetitive(account, fresh_candidate, history_file=global_history_file)
        assert is_fresh is False
