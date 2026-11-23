"""
Resrise Creator Swarm - End-to-End Automated Verification Suite
Validates:
1. Core creator configuration and accounts roster (R1)
2. Centralized affiliate mappings, EarnKaro subids, Amazon tags, and Telegram funnels (R1)
3. Keyword trigger detection across scripts/ig_replier.py and ig_replier.py for all 5 creators (R3)
4. Network engager configuration and persona prompts (R3)
5. Landing page asset integrity, local image paths, and ASCI disclosures (R2)
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
import pytest

from scripts.core.config import Settings
from scripts.core.utils import validate_account
from scripts.affiliate_mappings import (
    CREATOR_ACCOUNTS,
    TELEGRAM_CHANNELS,
    AMAZON_TRACKING_IDS,
    EARNKARO_SUBID_PATTERNS,
    UNIVERSAL_KEYWORDS,
    PERSONA_KEYWORDS,
    get_creator_telegram,
    get_earnkaro_subid,
    get_earnkaro_link,
    validate_earnkaro_link,
    get_amazon_tag,
    get_amazon_link,
    validate_amazon_link,
    get_creator_keywords,
    check_keyword_trigger,
    format_telegram_drop_message,
    get_creator_look_catalog,
    validate_all_creator_mappings,
    get_amazon_search_url,
    get_amazon_search_link,
    load_affiliate_config,
)
from scripts.ig_replier import (
    check_affiliate_trigger as scripts_check_affiliate_trigger,
    get_affiliate_trigger_details,
    AFFILIATE_KEYWORDS,
    TELEGRAM_CHANNELS as REPLIER_TELEGRAM_CHANNELS,
)
import ig_replier
from scripts.ig_network_engager import (
    get_account_profile,
    get_persona_prompt,
    generate_peer_comment,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]


class TestCreatorConfigurationAndRoster:
    """Verifies that all 5 creator accounts are fully registered and valid."""

    EXPECTED_CREATORS = [
        "avanyamehra",
        "mairamehraofficial",
        "iamgagankumar",
        "resrise",
        "gagankumarrocks",
    ]

    def test_settings_instagram_accounts_contains_all_5(self):
        settings = Settings()
        for account in self.EXPECTED_CREATORS:
            assert account in settings.instagram_accounts, f"Missing {account} in settings"

    def test_validate_account_succeeds_for_all_5(self):
        for account in self.EXPECTED_CREATORS:
            assert validate_account(account) == account
            assert validate_account(f"@{account}") == account

    def test_accounts_config_json_contains_all_5_with_metadata(self):
        config_path = PROJECT_DIR / "scripts" / "accounts_config.json"
        assert config_path.exists(), "scripts/accounts_config.json must exist"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        accounts = data.get("accounts", {})
        for account in self.EXPECTED_CREATORS:
            assert account in accounts, f"{account} missing in accounts_config.json"
            cfg = accounts[account]
            assert "telegram" in cfg, f"Missing telegram config for {account}"
            assert "affiliate" in cfg, f"Missing affiliate config for {account}"
            assert "trigger_keywords" in cfg, f"Missing trigger keywords for {account}"
            assert cfg["telegram"]["url"].startswith("https://t.me/")

    def test_validate_all_creator_mappings_passes(self):
        report = validate_all_creator_mappings()
        assert report["is_valid"] is True
        for account in self.EXPECTED_CREATORS:
            assert report["creators"][account]["status"] == "PASS"


class TestTelegramFunnelRouting:
    """Verifies Telegram channel destinations and drop formatting."""

    EXPECTED_TELEGRAM = {
        "avanyamehra": ("https://t.me/avanyamehra_luxe", "@avanyamehra_luxe"),
        "mairamehraofficial": ("https://t.me/mairamehraclub", "@mairamehraclub"),
        "iamgagankumar": ("https://t.me/gagankumar_menswear", "@gagankumar_menswear"),
        "resrise": ("https://t.me/resrise_studio", "@resrise_studio"),
        "gagankumarrocks": ("https://t.me/gagankumar_growth", "@gagankumar_growth"),
    }

    def test_canonical_telegram_urls(self):
        for account, (expected_url, expected_handle) in self.EXPECTED_TELEGRAM.items():
            tg = get_creator_telegram(account)
            assert tg["url"] == expected_url
            assert tg["handle"] == expected_handle

    def test_maira_alias_support(self):
        tg = get_creator_telegram("mairamehraofficial")
        assert "aliases" in tg
        assert "@MairaDrapes" in tg["aliases"] or "https://t.me/MairaDrapes" in tg["aliases"]

    def test_format_telegram_drop_message(self):
        msg = format_telegram_drop_message(
            account="mairamehraofficial",
            look_id="look1",
            title="Lavender Shimmer Organza Saree",
            price="₹2,299",
            earnkaro_url="https://topdeal.app.link/maira-lavender",
            amazon_url="https://www.amazon.in/dp/B08LAVORGANZA",
        )
        expected_tag = get_amazon_tag("mairamehraofficial")
        assert "Maira Mehra VIP Saree Club" in msg
        assert "Lavender Shimmer Organza Saree" in msg
        assert "subid=maira_saree_look1" in msg
        assert f"tag={expected_tag}" in msg
        assert "#affiliate" in msg


class TestAffiliateTrackingParameters:
    """Validates EarnKaro sub-ID patterns, Amazon tags, and link builders."""

    EXPECTED_AMAZON_TAGS = {
        "avanyamehra": "avanyamehra-21",
        "mairamehraofficial": "mairamehra-21",
        "iamgagankumar": "iamgagankumar-21",
        "resrise": "resriseagency-21",
        "gagankumarrocks": "gagankumarrocks-21",
    }

    EXPECTED_SUBID_PREFIXES = {
        "avanyamehra": "avanya_luxe_",
        "mairamehraofficial": "maira_saree_",
        "iamgagankumar": "gagan_mens_",
        "resrise": "resrise_studio_",
        "gagankumarrocks": "gagan_growth_",
    }

    def test_amazon_tracking_ids_and_links(self):
        for account in CREATOR_ACCOUNTS:
            tag = get_amazon_tag(account)
            assert tag.endswith("-21")

            url = get_amazon_link(account, "https://www.amazon.in/dp/B08SAMPLE")
            assert f"tag={tag}" in url
            assert validate_amazon_link(url, expected_account=account) is True

    def test_earnkaro_subid_generation_and_validation(self):
        for account, expected_prefix in self.EXPECTED_SUBID_PREFIXES.items():
            subid = get_earnkaro_subid(account, look_id="testlook")
            assert subid == f"{expected_prefix}testlook"

            url = get_earnkaro_link(account, "https://topdeal.app.link/deal123", look_id="festive01")
            assert f"subid={expected_prefix}festive01" in url
            assert validate_earnkaro_link(url, expected_account=account) is True

    def test_tampered_links_fail_validation(self):
        bad_amazon = "https://www.amazon.in/dp/B08SAMPLE?tag=someoneelse-99"
        assert validate_amazon_link(bad_amazon, expected_account="avanyamehra") is False

        bad_earnkaro = "https://topdeal.app.link/deal123?subid=unknown_fake_tag"
        assert validate_earnkaro_link(bad_earnkaro, expected_account="avanyamehra") is False

    def test_creator_look_catalog_contains_tracked_links(self):
        for account in CREATOR_ACCOUNTS:
            catalog = get_creator_look_catalog(account)
            assert len(catalog) >= 2, f"Expected at least 2 looks for {account}"
            for item in catalog:
                assert "earnkaro_tracked_url" in item
                assert validate_earnkaro_link(item["earnkaro_tracked_url"], expected_account=account)
                if item.get("amazon_url"):
                    assert "amazon_tracked_url" in item
                    assert validate_amazon_link(item["amazon_tracked_url"], expected_account=account)

    def test_amazon_search_url_and_fallback_link(self):
        search_url = get_amazon_search_url("emerald raw silk saree gold zari")
        assert "amazon.in/s?k=" in search_url
        assert "emerald" in search_url

        maira_tag = get_amazon_tag("mairamehraofficial")
        tracked_search = get_amazon_search_link("mairamehraofficial", "emerald raw silk saree gold zari")
        assert f"tag={maira_tag}" in tracked_search
        assert validate_amazon_link(tracked_search, expected_account="mairamehraofficial") is True

    def test_affiliate_config_json_loaded_and_valid(self):
        cfg = load_affiliate_config()
        assert "amazon_associates" in cfg
        assert "earnkaro" in cfg
        assert cfg["amazon_associates"]["primary_tag"].endswith("-21")
        assert "mairamehraofficial" in cfg["amazon_associates"]["tracking_ids"]

    def test_telegram_drops_queue_has_live_search_links(self):
        queue_path = PROJECT_DIR / "telegram_drops_queue.json"
        assert queue_path.exists()
        with open(queue_path, "r", encoding="utf-8") as f:
            drops = json.load(f)
        assert len(drops) >= 6
        for drop in drops:
            text = drop.get("drop_text", "")
            assert "#affiliate" in text
            assert "tag=" in text or "t.me/" in text
            # Ensure no dummy 404 ASIN placeholders remain
            assert "B08LAVORGANZA" not in text
            assert "B08KHANBLAZER" not in text



class TestKeywordTriggerDetection:
    """Validates trigger keyword parsing and routing for all creators."""

    REQUIRED_TRIGGERS = ["DRAPE", "LINK", "OUTFIT", "SAREE", "FIT"]

    def test_all_required_triggers_match_for_avanya(self):
        for trigger in self.REQUIRED_TRIGGERS:
            comment = f"Hi Avanya, can you share the {trigger} details please?!"
            rep = scripts_check_affiliate_trigger("avanyamehra", comment)
            assert rep is not None, f"Failed to match trigger {trigger} for avanyamehra"
            assert "avanyamehra_luxe" in rep
            assert "#affiliate" in rep

    def test_all_required_triggers_match_for_maira(self):
        for trigger in self.REQUIRED_TRIGGERS:
            comment = f"Love this drape! Where is the {trigger} from?"
            rep = scripts_check_affiliate_trigger("mairamehraofficial", comment)
            assert rep is not None, f"Failed to match trigger {trigger} for mairamehraofficial"
            assert "mairamehraclub" in rep
            assert "#affiliate" in rep

    def test_all_required_triggers_match_for_gagan(self):
        for trigger in self.REQUIRED_TRIGGERS:
            comment = f"Clean silhouette man! Send the {trigger} source."
            rep = scripts_check_affiliate_trigger("iamgagankumar", comment)
            assert rep is not None, f"Failed to match trigger {trigger} for iamgagankumar"
            assert "gagankumar_menswear" in rep
            assert "#affiliate" in rep

    def test_persona_specific_keywords(self):
        # Maira specific: lavender, organza, blouse
        rep_maira = scripts_check_affiliate_trigger("mairamehraofficial", "Which shop has this lavender organza?")
        assert rep_maira is not None

        # Gagan specific: linen, polo, beard
        rep_gagan = scripts_check_affiliate_trigger("iamgagankumar", "What beard oil and linen shirt is that?")
        assert rep_gagan is not None

        # Avanya specific: blazer, chic, satin
        rep_avanya = scripts_check_affiliate_trigger("avanyamehra", "Obsessed with this chic blazer!")
        assert rep_avanya is not None

        # Resrise specific: roster, scale, studio
        rep_resrise = scripts_check_affiliate_trigger("resrise", "How can we scale with your creator roster?")
        assert rep_resrise is not None
        assert "resrise_studio" in rep_resrise

        # Gagan Rocks specific: growth, systems
        rep_rocks = scripts_check_affiliate_trigger("gagankumarrocks", "Can you share the growth systems blueprint?")
        assert rep_rocks is not None
        assert "gagankumar_growth" in rep_rocks

    def test_root_ig_replier_matches_synchronously(self):
        rep = ig_replier.check_affiliate_trigger("avanyamehra", "Please send the OUTFIT link!")
        assert rep is not None
        assert "avanyamehra_luxe" in rep

    def test_trigger_details_payload(self):
        details = get_affiliate_trigger_details("mairamehraofficial", "Love the SAREE drape!")
        assert details is not None
        assert details["matched_keyword"] in ["SAREE", "DRAPE"]
        assert details["telegram_url"] == "https://t.me/mairamehraclub"
        assert "subid=maira_saree_" in details["affiliate_sample_url"]

    def test_generic_non_trigger_returns_none(self):
        assert scripts_check_affiliate_trigger("avanyamehra", "Good morning team!") is None
        assert scripts_check_affiliate_trigger("mairamehraofficial", "Beautiful day in Udaipur!") is None

    def test_no_false_positive_on_conversational_where_and_look(self):
        """Conversational 'where' and 'look' should NOT trigger affiliate links."""
        assert scripts_check_affiliate_trigger("avanyamehra", "Where was this photo taken?") is None
        assert scripts_check_affiliate_trigger("mairamehraofficial", "Look at that sunset!") is None
        assert scripts_check_affiliate_trigger("iamgagankumar", "Where is this shoot location?") is None
        assert scripts_check_affiliate_trigger("avanyamehra", "Look forward to your next reel!") is None

    def test_explicit_where_to_buy_intent_phrase_triggers(self):
        """Explicit intent phrase 'where to buy' triggers affiliate response."""
        res = scripts_check_affiliate_trigger("avanyamehra", "Where to buy this piece?")
        assert res is not None
        assert "t.me/avanyamehra_luxe" in res

    def test_author_handle_regex_bleed_prevention(self):
        """User handles containing dots/hyphens like @drape.studio must not trigger affiliate responses."""
        from scripts.ig_replier import PERSONA_FALLBACK_REPLIES, generate_reply_text

        # Passing formatted comment with handle containing trigger keyword
        assert scripts_check_affiliate_trigger("avanyamehra", "@drape.studio: Beautiful sunset!") is None
        assert scripts_check_affiliate_trigger("iamgagankumar", "@fit-guy: Amazing composition!") is None
        assert scripts_check_affiliate_trigger("mairamehraofficial", "@outfit.daily: Loved this post!") is None

        # generate_reply_text should return a persona fallback, NOT an affiliate link with t.me
        reply = generate_reply_text("avanyamehra", b"", "caption", "@drape.studio: Beautiful photo!")
        assert "t.me" not in reply
        assert any(reply == fb for fb in PERSONA_FALLBACK_REPLIES["avanyamehra"])

        reply_fit = generate_reply_text("iamgagankumar", b"", "caption", "@fit-guy: Looking great man!")
        assert "t.me" not in reply_fit
        assert any(reply_fit == fb for fb in PERSONA_FALLBACK_REPLIES["iamgagankumar"])


class TestNetworkEngagerConfiguration:
    """Verifies that ig_network_engager connects to creator profiles."""

    def test_get_account_profile_loads_metadata(self):
        for account in CREATOR_ACCOUNTS:
            profile = get_account_profile(account)
            assert profile, f"Could not load profile for {account}"
            assert "display_name" in profile
            assert "niche" in profile
            assert "pillars" in profile

    def test_get_persona_prompt_generates_tailored_prompt(self):
        for account in CREATOR_ACCOUNTS:
            prompt = get_persona_prompt(account)
            assert account in prompt
            assert "peer comment" in prompt

    def test_generate_peer_comment_returns_nonempty_string(self):
        for account in CREATOR_ACCOUNTS:
            comment = generate_peer_comment(account, b"", "Great architectural tailoring!")
            assert isinstance(comment, str)
            assert len(comment) > 5


class TestLandingPageAssetIntegrity:
    """Verifies frontend HTML/JS/CSS integrity and asset resolution."""

    def test_app_js_syntax_clean(self):
        node_bin = shutil.which("node") or (r"C:\Program Files\nodejs\node.exe" if os.path.exists(r"C:\Program Files\nodejs\node.exe") else None)
        if not node_bin:
            pytest.skip("Node.js binary not found for syntax check")
        res = subprocess.run([node_bin, "-c", str(PROJECT_DIR / "app.js")], capture_output=True, text=True)
        assert res.returncode == 0, f"app.js syntax error: {res.stderr}"

    def test_data_js_syntax_clean(self):
        node_bin = shutil.which("node") or (r"C:\Program Files\nodejs\node.exe" if os.path.exists(r"C:\Program Files\nodejs\node.exe") else None)
        if not node_bin:
            pytest.skip("Node.js binary not found for syntax check")
        res = subprocess.run([node_bin, "-c", str(PROJECT_DIR / "data.js")], capture_output=True, text=True)
        assert res.returncode == 0, f"data.js syntax error: {res.stderr}"

    def test_data_js_contains_all_5_creators_with_telegrams(self):
        with open(PROJECT_DIR / "data.js", "r", encoding="utf-8") as f:
            content = f.read()
        for tg_url in [
            "https://t.me/avanyamehra_luxe",
            "https://t.me/mairamehraclub",
            "https://t.me/gagankumar_menswear",
            "https://t.me/resrise_studio",
            "https://t.me/gagankumar_growth",
        ]:
            assert tg_url in content, f"Missing {tg_url} in data.js"

    def test_local_assets_exist_on_disk(self):
        assets_dir = PROJECT_DIR / "assets"
        required_images = [
            "avanya_hero.jpg",
            "avanya_paris.jpg",
            "avanya_milan.jpg",
            "maira_hero.jpg",
            "maira_lavender.jpg",
            "maira_saree.jpg",
            "gagan_hero.jpg",
            "gagan_linen.jpg",
            "gagan_blazer.jpg",
        ]
        for img_name in required_images:
            img_path = assets_dir / img_name
            assert img_path.exists(), f"Missing required asset {img_name}"
            assert img_path.stat().st_size > 1000, f"Asset {img_name} appears empty"

    def test_all_creator_landing_pages_exist(self):
        expected_pages = [
            "index.html",
            "avanyamehra.html",
            "mairamehra.html",
            "iamgagankumar.html",
            "resrise.html",
            "gagankumarrocks.html",
        ]
        for page_name in expected_pages:
            page_path = PROJECT_DIR / page_name
            assert page_path.exists(), f"Missing landing page {page_name}"
            text = page_path.read_text(encoding="utf-8")
            assert "<!DOCTYPE html>" in text
            assert '<meta name="viewport"' in text
            assert "#affiliate" in text

    def test_telegram_channels_in_index_html(self):
        index_text = (PROJECT_DIR / "index.html").read_text(encoding="utf-8")
        assert "https://t.me/resrise_studio" in index_text
        assert "https://t.me/avanyamehra_luxe" in index_text
        assert "https://t.me/mairamehraclub" in index_text
        assert "https://t.me/gagankumar_menswear" in index_text
        assert "https://t.me/gagankumar_growth" in index_text
        assert 'type="module"' in index_text


class TestIgReplierInternals:
    """Tests the comment replier internal helper functions and caching."""

    def test_hash_comment(self):
        from scripts.ig_replier import hash_comment
        h1 = hash_comment("fashion_fan", "Where is this saree from?")
        h2 = hash_comment("fashion_fan", "Where is this saree from?")
        h3 = hash_comment("other_user", "Where is this saree from?")
        assert len(h1) == 16
        assert h1 == h2
        assert h1 != h3

    def test_cache_save_and_load(self, tmp_path):
        from scripts.ig_replier import load_replied_cache, save_replied_cache
        cache_file = tmp_path / "replied_cache.json"
        assert load_replied_cache(str(cache_file)) == set()

        items = {"hash1", "hash2", "hash3"}
        save_replied_cache(str(cache_file), items)
        loaded = load_replied_cache(str(cache_file))
        assert loaded == items

    def test_get_chrome_profile_dir_and_logging(self, tmp_path):
        from scripts.ig_replier import get_chrome_profile_dir, log_activity
        profile_dir = get_chrome_profile_dir("avanyamehra")
        assert "avanyamehra" in profile_dir

        log_file = tmp_path / "activity.log"
        log_activity(str(log_file), "avanyamehra", "Test log entry message")
        assert log_file.exists()
        assert "Test log entry message" in log_file.read_text(encoding="utf-8")

    def test_generate_reply_text_fallback_and_affiliate(self):
        from scripts.ig_replier import generate_reply_text
        # Trigger comment returns affiliate reply
        reply = generate_reply_text("avanyamehra", b"", "caption", "What OUTFIT is that?")
        assert reply != ""
        assert "avanyamehra_luxe" in reply

        # Non-trigger comment returns persona fallback reply
        reply_fallback = generate_reply_text("avanyamehra", b"", "caption", "Great vibes")
        assert reply_fallback != ""

    def test_mock_dom_extraction_and_response_detection(self):
        from scripts.ig_replier import extract_comment_parts, is_already_responded

        class MockRow:
            def evaluate(self, script, *args):
                if "authorLink" in script:
                    return {"author": "style_user", "body": "Where to get this drape? 2h Reply"}
                if "targetAccount" in script:
                    return False
                return False

            def inner_text(self):
                return "style_user Where to get this drape? 2h Reply"

        author, body = extract_comment_parts(MockRow())
        assert author == "style_user"
        assert "drape" in body

        already = is_already_responded(MockRow(), "avanyamehra")
        assert already is False


class TestIgNetworkEngagerInternals:
    """Tests the network engager internal helper functions and caching."""

    def test_load_accounts_config(self):
        from scripts.ig_network_engager import load_accounts_config
        cfg = load_accounts_config()
        assert "avanyamehra" in cfg
        assert "iamgagankumar" in cfg

    def test_engager_cache_save_and_load(self, tmp_path):
        from scripts.ig_network_engager import load_commented_cache, save_commented_cache
        cache_file = tmp_path / "engager_cache.json"
        assert load_commented_cache(str(cache_file)) == set()

        signatures = {"sig1", "sig2"}
        save_commented_cache(str(cache_file), signatures)
        loaded = load_commented_cache(str(cache_file))
        assert loaded == signatures

    def test_mock_article_evaluation(self):
        from scripts.ig_network_engager import is_post_from_followed_account, has_user_already_commented

        class MockFollowedArticle:
            def evaluate(self, script, *args):
                if "targetAccount" in script:
                    return False
                return {"author": "vogue_india", "hasFollowBtn": False, "isSponsored": False}

        class MockStrangerArticle:
            def evaluate(self, script, *args):
                if "targetAccount" in script:
                    return True
                return {"author": "random_stranger", "hasFollowBtn": True, "isSponsored": False}

        class MockSponsoredArticle:
            def evaluate(self, script, *args):
                return {"author": "brand_ad", "hasFollowBtn": False, "isSponsored": True}

        class MockEmptyArticle:
            def evaluate(self, script, *args):
                return {"author": "", "hasFollowBtn": False, "isSponsored": False}

        class MockErrorArticle:
            def evaluate(self, script, *args):
                raise RuntimeError("DOM error")

        is_followed, author = is_post_from_followed_account(MockFollowedArticle())
        assert is_followed is True
        assert author == "vogue_india"

        is_stranger, stranger_author = is_post_from_followed_account(MockStrangerArticle())
        assert is_stranger is False

        is_sponsored, _ = is_post_from_followed_account(MockSponsoredArticle())
        assert is_sponsored is False

        is_empty, _ = is_post_from_followed_account(MockEmptyArticle())
        assert is_empty is False

        is_err, _ = is_post_from_followed_account(MockErrorArticle())
        assert is_err is False

        has_commented_false = has_user_already_commented(MockFollowedArticle(), "avanyamehra")
        assert has_commented_false is False

        has_commented_true = has_user_already_commented(MockStrangerArticle(), "avanyamehra")
        assert has_commented_true is True

        has_commented_err = has_user_already_commented(MockErrorArticle(), "avanyamehra")
        assert has_commented_err is False

    def test_engager_log_and_profile_dir(self, tmp_path):
        from scripts.ig_network_engager import log_activity, get_chrome_profile_dir, load_commented_cache
        log_f = tmp_path / "engager.log"
        log_activity(str(log_f), "iamgagankumar", "Engager log message")
        assert log_f.exists()

        pdir = get_chrome_profile_dir("iamgagankumar")
        assert "iamgagankumar" in pdir

        bad_cache = tmp_path / "bad_cache.json"
        bad_cache.write_text("invalid json", encoding="utf-8")
        assert load_commented_cache(str(bad_cache)) == set()


class TestAffiliateMappingsEdgeCases:
    """Verifies edge cases and error handling in affiliate_mappings."""

    def test_normalize_empty_handle(self):
        from scripts.affiliate_mappings import normalize_account_handle
        assert normalize_account_handle("") == ""
        assert normalize_account_handle("   ") == ""
        assert normalize_account_handle("@AvanyaMehra  ") == "avanyamehra"

    def test_unknown_creator_exceptions(self):
        with pytest.raises(KeyError):
            get_creator_telegram("nonexistent")
        with pytest.raises(KeyError):
            get_earnkaro_subid("nonexistent")
        with pytest.raises(KeyError):
            get_amazon_tag("nonexistent")

    def test_validate_empty_and_invalid_links(self):
        assert validate_earnkaro_link("") is False
        assert validate_earnkaro_link("https://example.com/item") is False
        assert validate_earnkaro_link("https://example.com/item?subid=") is False

        assert validate_amazon_link("") is False
        assert validate_amazon_link("https://amazon.in/dp/123") is False
        assert validate_amazon_link("https://amazon.in/dp/123?tag=") is False
        assert validate_amazon_link("https://amazon.in/dp/123?tag=badtag") is False

    def test_check_keyword_trigger_unknown_account_or_no_match(self):
        assert check_keyword_trigger("unknown_acc", "send link") is None
        assert check_keyword_trigger("avanyamehra", "hello there") is None

    def test_check_keyword_trigger_with_specific_look_id(self):
        res = check_keyword_trigger("avanyamehra", "love this blazer!", look_id="look2")
        assert res is not None
        assert "subid=avanya_luxe_look2" in res["affiliate_sample_url"]


class TestReplierScenarios:
    """Tests additional replier scenarios to ensure robust coverage."""

    def test_parse_account_helper(self):
        from scripts.ig_replier import parse_account
        assert parse_account("avanyamehra") == "avanyamehra"
        assert parse_account("@MairaMehraOfficial") == "mairamehraofficial"
        with pytest.raises(Exception):
            parse_account("unregistered_creator")

    def test_generate_reply_all_accounts(self):
        from scripts.ig_replier import generate_reply_text
        for acc in CREATOR_ACCOUNTS:
            rep = generate_reply_text(acc, b"", "caption text", "where is the outfit from?")
            assert len(rep) > 0

            fallback = generate_reply_text(acc, b"", "caption text", "love your page")
            assert len(fallback) > 0

    def test_cache_corrupt_file_handling(self, tmp_path):
        from scripts.ig_replier import load_replied_cache
        bad_cache = tmp_path / "bad_cache.json"
        bad_cache.write_text("not json content!", encoding="utf-8")
        assert load_replied_cache(str(bad_cache)) == set()

    def test_is_already_responded_variations(self):
        from scripts.ig_replier import is_already_responded

        class MockSelfComment:
            def evaluate(self, script, *args):
                return True

        assert is_already_responded(MockSelfComment(), "avanyamehra") is True

        class MockErrComment:
            def evaluate(self, script, *args):
                raise RuntimeError("Evaluation failed")

        assert is_already_responded(MockErrComment(), "avanyamehra") is False


class TestCoreLoggingAndBrowser:
    """Verifies core logging and browser configuration modules."""

    def test_configure_logging_console_and_file(self, tmp_path):
        from scripts.core.logging import configure_logging, get_logger
        log_file = tmp_path / "system.log"
        configure_logging(log_file=log_file, level="DEBUG", json_output=False)
        logger = get_logger("test.logger")
        logger.info("Console formatted test log")

        json_log = tmp_path / "system_json.log"
        configure_logging(log_file=json_log, level="INFO", json_output=True)
        json_logger = get_logger("test.json")
        json_logger.info("JSON formatted test log")

    def test_activity_logger(self, tmp_path):
        from scripts.core.logging import ActivityLogger
        log_path = tmp_path / "creator_activity.log"
        logger = ActivityLogger("avanyamehra", log_file=log_path)
        logger.log("Posting lookbook drop")
        logger.debug("Debug details")
        logger.warning("Rate limit approaching")
        logger.error("Network hiccup")
        logger.success("Lookbook drop published successfully")

        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert "Posting lookbook drop" in content
        assert "[@avanyamehra]" in content

    def test_browser_config_defaults_and_overrides(self):
        from scripts.core.browser import BrowserConfig, BrowserManager
        cfg = BrowserConfig(headless=True, channel="chromium")
        assert cfg.headless is True
        assert cfg.viewport["width"] == 1150
        assert any("--window-position=80,50" in a for a in cfg.args)

        bm = BrowserManager("avanyamehra", config=cfg)
        assert bm.account == "avanyamehra"
        assert "avanyamehra" in str(bm.profile_dir)
        args = bm._get_launch_args()
        assert len(args) >= 3
