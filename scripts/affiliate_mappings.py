"""
Resrise Studio - Centralized Affiliate & Telegram Monetization Mappings
Single source of truth for Telegram channels, EarnKaro sub-IDs, Amazon tracking tags,
and keyword trigger routing across the creator swarm.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = (
    os.path.dirname(SCRIPT_DIR)
    if os.path.basename(SCRIPT_DIR).lower() == "scripts"
    else SCRIPT_DIR
)


def load_affiliate_config() -> dict[str, Any]:
    """Loads affiliate configuration from affiliate_config.json if available."""
    candidates = [
        os.path.join(PROJECT_DIR, "affiliate_config.json"),
        os.path.join(SCRIPT_DIR, "affiliate_config.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


# Roster of all 5 target creator accounts
CREATOR_ACCOUNTS: tuple[str, ...] = (
    "avanyamehra",
    "mairamehraofficial",
    "iamgagankumar",
    "resrise",
    "gagankumarrocks",
)

# Canonical Telegram VIP & Broadcast Destinations
TELEGRAM_CHANNELS: dict[str, dict[str, Any]] = {
    "avanyamehra": {
        "display_name": "Avanya Mehra Luxe Vault",
        "url": "https://t.me/avanyamehra_luxe",
        "handle": "@avanyamehra_luxe",
        "linktree": "https://linktr.ee/avanyamehra",
        "network": "EarnKaro (Nykaa/Zara) & Amazon Associates",
    },
    "mairamehraofficial": {
        "display_name": "Maira Mehra VIP Saree Club",
        "url": "https://t.me/mairamehraclub",
        "handle": "@mairamehraclub",
        "aliases": ["@MairaDrapes", "https://t.me/MairaDrapes"],
        "linktree": "https://linktr.ee/mairamehraofficial",
        "network": "EarnKaro (Ajio/Myntra/Meesho) & Amazon Associates",
    },
    "iamgagankumar": {
        "display_name": "Gagan Kumar Men's Capsule Club",
        "url": "https://t.me/gagankumar_menswear",
        "handle": "@gagankumar_menswear",
        "linktree": "https://linktr.ee/iamgagankumar",
        "network": "Amazon Associates & EarnKaro (Myntra/Ajio)",
    },
    "resrise": {
        "display_name": "Resrise Studio VIP Roster & Hub",
        "url": "https://t.me/resrise_studio",
        "handle": "@resrise_studio",
        "linktree": "https://linktr.ee/resrisestudio",
        "network": "Resrise Studio B2B Retainers & Production Packages",
    },
    "gagankumarrocks": {
        "display_name": "Gagan Kumar Media Systems",
        "url": "https://t.me/gagankumar_growth",
        "handle": "@gagankumar_growth",
        "linktree": "https://linktr.ee/gagankumarrocks",
        "network": "Media Systems, Creator Software & Consulting",
    },
}

# Amazon Associates Tracking ID Architecture (India Store Tag -21)
AMAZON_TRACKING_IDS: dict[str, str] = {
    "avanyamehra": "avanyamehra-21",
    "mairamehraofficial": "mairamehra-21",
    "iamgagankumar": "iamgagankumar-21",
    "resrise": "resriseagency-21",
    "gagankumarrocks": "gagankumarrocks-21",
}

# EarnKaro Sub-ID Attribution Architecture (&subid=...)
EARNKARO_SUBID_PATTERNS: dict[str, str] = {
    "avanyamehra": "avanya_luxe_{look_id}",
    "mairamehraofficial": "maira_saree_{look_id}",
    "iamgagankumar": "gagan_mens_{look_id}",
    "resrise": "resrise_studio_{look_id}",
    "gagankumarrocks": "gagan_growth_{look_id}",
}

# Universal high-intent intent keywords across all creators
UNIVERSAL_KEYWORDS: list[str] = [
    "drape",
    "drapes",
    "link",
    "links",
    "outfit",
    "outfits",
    "saree",
    "sarees",
    "fit",
    "fits",
    "dress",
    "suit",
    "blazer",
    "details",
    "where to buy",
    "buy",
    "price",
    "source",
    "brand",
    "shop",
    "deets",
]

# Persona-specific high-converting trigger keywords
PERSONA_KEYWORDS: dict[str, list[str]] = {
    "avanyamehra": [
        "blazer", "chic", "satin", "zara", "mango", "loafers", "suit",
        "dress", "trench", "halter", "silhouette", "couture", "luxe",
    ],
    "mairamehraofficial": [
        "drape", "saree", "saris", "lavender", "organza", "blouse",
        "jhumka", "meesho", "ajio", "silk", "pallu", "tissue", "festive",
    ],
    "iamgagankumar": [
        "linen", "polo", "beard", "watch", "scent", "shave", "style",
        "capsule", "knit", "jacket", "trousers", "minimalist", "fragrance",
    ],
    "resrise": [
        "roster", "scale", "studio", "agency", "creator", "production",
        "retainer", "pilot", "campaign",
    ],
    "gagankumarrocks": [
        "growth", "systems", "founder", "blueprint", "media", "scale",
        "framework", "flywheel", "playbook",
    ],
}

# Master Curated Lookbook Catalog for Instant Affiliate Monetization
# All Amazon URLs use reliable search queries on amazon.in that NEVER 404
CREATOR_LOOK_CATALOG: dict[str, list[dict[str, Any]]] = {
    "avanyamehra": [
        {
            "look_id": "look1",
            "title": "Tailored Double-Breasted Charcoal Structured Wool Blazer",
            "store": "Amazon Fashion / Ajio Luxe / Zara Dupe",
            "price": "₹4,299",
            "search_keywords": "women double breasted oversized tailored blazer",
            "base_url": "https://topdeal.app.link/avanya-blazer",
            "amazon_url": "https://www.amazon.in/s?k=women+double+breasted+oversized+tailored+blazer",
        },
        {
            "look_id": "look2",
            "title": "Minimalist Champagne Gold Silk Satin Column Slip Maxi Dress",
            "store": "Mango / Nykaa Fashion / Amazon",
            "price": "₹2,899",
            "search_keywords": "satin silk column slip maxi dress women",
            "base_url": "https://topdeal.app.link/avanya-satin-dress",
            "amazon_url": "https://www.amazon.in/s?k=satin+silk+column+slip+maxi+dress+women",
        },
        {
            "look_id": "look3",
            "title": "Sculptural Italian Leather Minimalist Shoulder Clutch",
            "store": "Amazon Fashion / Ajio Luxe",
            "price": "₹3,990",
            "search_keywords": "minimalist leather shoulder clutch bag women",
            "base_url": "https://topdeal.app.link/avanya-leather-clutch",
            "amazon_url": "https://www.amazon.in/s?k=minimalist+leather+shoulder+clutch+bag+women",
        },
    ],
    "mairamehraofficial": [
        {
            "look_id": "look1",
            "title": "Pastel Blush Embroidered Organza Saree with Scalloped Zari Border",
            "store": "Meesho / Ajio Ethnic / Amazon Fashion",
            "price": "₹2,199",
            "search_keywords": "organza silk floral embroidered saree with scalloped border",
            "base_url": "https://topdeal.app.link/maira-organza-saree",
            "amazon_url": "https://www.amazon.in/s?k=organza+silk+floral+embroidered+saree+with+scalloped+border",
        },
        {
            "look_id": "look2",
            "title": "SWORNOF Royal Emerald Soft Kanjivaram Silk Saree (Rich Zari Pallu)",
            "store": "Amazon Bestseller (ASIN: B0D96G98KY) / Myntra Silk",
            "price": "₹3,499",
            "search_keywords": "soft kanjivaram silk saree rich gold zari pallu wedding",
            "base_url": "https://topdeal.app.link/maira-kanjivaram-silk",
            "amazon_url": "https://www.amazon.in/dp/B0D96G98KY",
        },
        {
            "look_id": "look3",
            "title": "Zaveri Pearls Gold-Plated Kundan & Pearls Bridal Choker Set",
            "store": "Amazon Bestseller (ASIN: B07QBCC7NW - 3,500+ Ratings)",
            "price": "₹749",
            "search_keywords": "zaveri pearls gold kundan choker necklace set",
            "base_url": "https://topdeal.app.link/maira-kundan-choker",
            "amazon_url": "https://www.amazon.in/dp/B07QBCC7NW",
        },
    ],
    "iamgagankumar": [
        {
            "look_id": "look1",
            "title": "Pure French Linen Relaxed Camp Collar Casual Shirt (Sage Green / Sand)",
            "store": "Amazon Fashion / The Bear House / Myntra",
            "price": "₹2,799",
            "search_keywords": "pure linen camp collar long sleeve shirt men",
            "base_url": "https://topdeal.app.link/gagan-linen-shirt",
            "amazon_url": "https://www.amazon.in/s?k=pure+linen+camp+collar+long+sleeve+shirt+men",
        },
        {
            "look_id": "look2",
            "title": "Bella Vita Luxury CEO Man & Date Long-Lasting EDP Combo",
            "store": "Amazon Bestseller (ASIN: B0DBZTZP67) / Luxury Fragrance",
            "price": "₹649",
            "search_keywords": "bella vita luxury ceo man date perfume edp",
            "base_url": "https://topdeal.app.link/gagan-perfume-edp",
            "amazon_url": "https://www.amazon.in/dp/B0DBZTZP67",
        },
        {
            "look_id": "look3",
            "title": "Italian-Cut Unstructured Navy Wool Travel Blazer",
            "store": "Amazon Men / Zara / Van Heusen",
            "price": "₹5,499",
            "search_keywords": "navy unstructured blazer men",
            "base_url": "https://topdeal.app.link/gagan-navy-blazer",
            "amazon_url": "https://www.amazon.in/s?k=navy+unstructured+blazer+men",
        },
    ],
    "resrise": [
        {
            "look_id": "service1",
            "title": "100W Bi-Color COB Continuous Studio Video Light with Bowens Softbox",
            "store": "Amazon Creator Gear / Godox / Digitek",
            "price": "₹11,999",
            "search_keywords": "cob continuous video light 100w bowens mount softbox",
            "base_url": "https://topdeal.app.link/resrise-studio-light",
            "amazon_url": "https://www.amazon.in/s?k=cob+continuous+video+light+100w+bowens+mount+softbox",
        },
        {
            "look_id": "service2",
            "title": "Resrise Studio Creative Retainer & Autonomous Virtual Muse Licensing",
            "store": "Resrise Agency Desk / Amazon Pro",
            "price": "₹2,50,000/mo",
            "search_keywords": "hasselblad camera lens professional photography",
            "base_url": "https://topdeal.app.link/resrise-retainer",
            "amazon_url": "https://www.amazon.in/s?k=hasselblad+camera+lens+professional+photography",
        },
    ],
    "gagankumarrocks": [
        {
            "look_id": "blueprint1",
            "title": "Cardioid Dynamic Studio Podcast Microphone with USB / XLR & Touch Mute",
            "store": "Amazon Creator Tech / Fifine / Maono",
            "price": "₹6,499",
            "search_keywords": "dynamic studio podcast microphone usb xlr cardioid",
            "base_url": "https://topdeal.app.link/gagan-creator-mic",
            "amazon_url": "https://www.amazon.in/s?k=dynamic+studio+podcast+microphone+usb+xlr+cardioid",
        },
        {
            "look_id": "blueprint2",
            "title": "Compact 75% Wireless Hot-Swappable Mechanical Keyboard with RGB",
            "store": "Amazon Tech / Keychron / Royal Kludge",
            "price": "₹5,299",
            "search_keywords": "wireless mechanical keyboard 75 percent hot swappable",
            "base_url": "https://topdeal.app.link/gagan-mechanical-keyboard",
            "amazon_url": "https://www.amazon.in/s?k=wireless+mechanical+keyboard+75+percent+hot+swappable",
        },
    ],
}

# Persona-specific automated responses (Clean bio prompts without raw https:// URLs to prevent spam filters)
AFFILIATE_RESPONSES: dict[str, list[str]] = {
    "avanyamehra": [
        "Here's the look breakdown ✨ Curated outfit & styling links pinned in bio (t.me/avanyamehra_luxe) 🤍 #affiliate",
        "Loved this silhouette? 🤍 Direct styling & luxury partner pieces are linked in my bio vault (t.me/avanyamehra_luxe) ✨ #affiliate",
        "Full outfit details & styling curation are up via the link in my bio (t.me/avanyamehra_luxe) ✨ #affiliate",
        "Sent you the look details! High-fashion piece links & dupes pinned in my bio (t.me/avanyamehra_luxe) 🤍 #affiliate",
    ],
    "mairamehraofficial": [
        "Sent you the drape details! 🌸 Full saree & jewelry sources are live via our bio link (t.me/mairamehraclub) ✨ #affiliate",
        "Loved this drape? 🌸 Direct saree source & jewelry links are pinned in our bio club (t.me/mairamehraclub) ✨ #affiliate",
        "Here's the outfit curation! Tap our bio link to grab the direct saree details (t.me/mairamehraclub) 🌸 #affiliate",
        "All saree draping notes & matching blouse/jewelry links are pinned in our bio link (t.me/mairamehraclub) 🤍 #affiliate",
    ],
    "iamgagankumar": [
        "Got you covered brother! ⚡ Clean fit & grooming links pinned in the bio link (t.me/gagankumar_menswear) #affiliate",
        "Tailored fit breakdown & direct pieces are linked in my bio (t.me/gagankumar_menswear) ⚡ #affiliate",
        "Here's the outfit curation! Full capsule breakdown & source links in bio (t.me/gagankumar_menswear) ⚡ #affiliate",
        "Fit details & grooming essentials ready! Grab direct links in my bio (t.me/gagankumar_menswear) ⚡ #affiliate",
    ],
    "resrise": [
        "Thank you! Full creative campaign breakdown & studio booking info are linked in bio (t.me/resrise_studio) ✨",
        "Agency & editorial inquiries: connect with our team directly via our bio link (t.me/resrise_studio) ✨",
        "Interested in creator roster collaborations? Access our partner portal in bio (t.me/resrise_studio) ✨",
    ],
    "gagankumarrocks": [
        "Appreciate it! Full creator media systems blueprint & automation docs in bio (t.me/gagankumar_growth) 🚀",
        "Growth playbook & agency scaling breakdown are pinned via our bio link (t.me/gagankumar_growth) ⚡",
        "Grab the full brand growth system & free templates inside our bio portal (t.me/gagankumar_growth) 🚀",
    ],
}


def normalize_account_handle(account: str) -> str:
    """Strips leading '@' and whitespace, lowercases account name."""
    if not account:
        return ""
    return account.strip().lstrip("@").lower()


def get_creator_telegram(account: str) -> dict[str, Any]:
    """
    Returns canonical Telegram channel metadata for the specified account:
    {'display_name': str, 'url': str, 'handle': str, 'linktree': str, 'network': str}
    """
    clean_account = normalize_account_handle(account)
    if clean_account not in TELEGRAM_CHANNELS:
        raise KeyError(f"Unknown creator account '{account}'. Must be one of {CREATOR_ACCOUNTS}")
    return dict(TELEGRAM_CHANNELS[clean_account])


def get_earnkaro_subid(account: str, look_id: str = "default") -> str:
    """Generates EarnKaro sub-ID attribution string for given account and look."""
    clean_account = normalize_account_handle(account)
    config = load_affiliate_config()
    ek_cfg = config.get("earnkaro", {})
    subid_patterns = ek_cfg.get("subid_patterns", {})
    pattern = subid_patterns.get(clean_account) or EARNKARO_SUBID_PATTERNS.get(clean_account)
    if not pattern:
        raise KeyError(f"Unknown creator account '{account}' for EarnKaro sub-ID.")
    safe_look = re.sub(r"[^a-zA-Z0-9_-]", "", look_id or "default")
    return pattern.format(look_id=safe_look)


def get_earnkaro_link(account: str, target_url: str, look_id: str = "default") -> str:
    """
    Formats a target URL or EarnKaro profit link with the creator's tracked sub-ID.
    Appends or replaces &subid=<creator_subid>.
    """
    subid = get_earnkaro_subid(account, look_id)
    parsed = urllib.parse.urlparse(target_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    qs["subid"] = [subid]
    new_query = urllib.parse.urlencode(qs, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))


def validate_earnkaro_link(url: str, expected_account: str | None = None) -> bool:
    """
    Validates that an EarnKaro link carries a valid sub-ID query parameter,
    optionally matching the expected creator attribution pattern.
    """
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    subids = qs.get("subid")
    if not subids or not subids[0]:
        return False
    
    if expected_account:
        clean_account = normalize_account_handle(expected_account)
        expected_pattern_prefix = EARNKARO_SUBID_PATTERNS.get(clean_account, "").split("{")[0]
        if not expected_pattern_prefix or not subids[0].startswith(expected_pattern_prefix):
            return False
            
    return True


def get_amazon_tag(account: str) -> str:
    """Returns the Amazon Associates tracking ID for the account, checking affiliate_config.json first."""
    clean_account = normalize_account_handle(account)
    config = load_affiliate_config()
    amz_cfg = config.get("amazon_associates", {})
    tracking_ids = amz_cfg.get("tracking_ids", {})
    if clean_account in tracking_ids and tracking_ids[clean_account]:
        return tracking_ids[clean_account]
    if clean_account not in AMAZON_TRACKING_IDS:
        raise KeyError(f"Unknown creator account '{account}' for Amazon Associates tag.")
    return AMAZON_TRACKING_IDS[clean_account]


def get_amazon_link(account: str, target_url: str) -> str:
    """
    Formats an Amazon destination URL with the creator's Associates tracking tag.
    Appends or replaces ?tag=<amazon_tag>.
    """
    tag = get_amazon_tag(account)
    parsed = urllib.parse.urlparse(target_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    qs["tag"] = [tag]
    new_query = urllib.parse.urlencode(qs, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))


def get_amazon_search_url(keywords: str) -> str:
    """
    Generates a valid Amazon.in search/category URL for given product keywords.
    Guarantees a live shopping page with ZERO 404 errors.
    """
    clean_kws = re.sub(r"\s+", " ", keywords.strip())
    encoded = urllib.parse.quote_plus(clean_kws)
    return f"https://www.amazon.in/s?k={encoded}"


def get_amazon_search_link(account: str, keywords: str) -> str:
    """Generates a tracked Amazon.in search URL with creator's Associate tag."""
    base_search = get_amazon_search_url(keywords)
    return get_amazon_link(account, base_search)


def validate_amazon_link(url: str, expected_account: str | None = None) -> bool:
    """
    Validates that an Amazon link carries a valid Associates tag parameter,
    optionally verifying that it matches the expected account tag with -21 suffix.
    """
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    tags = qs.get("tag")
    if not tags or not tags[0]:
        return False
        
    tag = tags[0]
    if not tag.endswith("-21"):
        return False
        
    if expected_account:
        clean_account = normalize_account_handle(expected_account)
        expected_tag = get_amazon_tag(clean_account)
        if tag != expected_tag:
            return False
            
    return True


def get_creator_keywords(account: str) -> list[str]:
    """Returns combined list of universal and creator-specific trigger keywords."""
    clean_account = normalize_account_handle(account)
    persona_kws = PERSONA_KEYWORDS.get(clean_account, [])
    seen = set()
    result = []
    for kw in UNIVERSAL_KEYWORDS + persona_kws:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            result.append(kw_lower)
    return result


def check_keyword_trigger(
    account: str,
    comment_text: str,
    look_id: str | None = None,
) -> dict[str, Any] | None:
    """
    Detects trigger keywords (DRAPE, LINK, OUTFIT, SAREE, FIT, etc.) in comment_text.
    Returns routing response dict or None.
    """
    clean_account = normalize_account_handle(account)
    if clean_account not in CREATOR_ACCOUNTS:
        return None

    text_without_handles = re.sub(r"@[a-zA-Z0-9._-]+(?::\s*|\b)", " ", comment_text)
    clean_comment = text_without_handles.lower()

    keywords = get_creator_keywords(clean_account)
    sorted_keywords = sorted(keywords, key=len, reverse=True)

    pattern = r"\b(" + "|".join(re.escape(k) for k in sorted_keywords) + r")\b"
    match = re.search(pattern, clean_comment)
    if not match:
        return None

    matched_kw = match.group(1).upper()
    telegram_info = get_creator_telegram(clean_account)
    
    replies = AFFILIATE_RESPONSES.get(clean_account, [])
    reply_text = replies[0] if replies else f"Find details on Telegram: {telegram_info['url']} #affiliate"

    looks = CREATOR_LOOK_CATALOG.get(clean_account, [])
    selected_look = None
    if look_id and looks:
        for l in looks:
            if l.get("look_id") == look_id:
                selected_look = l
                break
    if not selected_look and looks:
        selected_look = looks[0]
        
    sample_earnkaro = ""
    sample_amazon = ""
    if selected_look:
        lid = selected_look.get("look_id", "look1")
        sample_earnkaro = get_earnkaro_link(clean_account, selected_look["base_url"], look_id=lid)
        sample_amazon = get_amazon_link(clean_account, selected_look["amazon_url"])

    return {
        "account": clean_account,
        "matched_keyword": matched_kw,
        "reply_text": reply_text,
        "telegram_url": telegram_info["url"],
        "telegram_handle": telegram_info["handle"],
        "affiliate_sample_url": sample_earnkaro,
        "amazon_sample_url": sample_amazon,
    }


def format_telegram_drop_message(
    account: str,
    look_id: str,
    title: str,
    price: str,
    earnkaro_url: str,
    amazon_url: str | None = None,
) -> str:
    """
    Formats a high-converting Telegram channel drop message with ASCI #affiliate disclosure.
    """
    clean_account = normalize_account_handle(account)
    telegram_info = get_creator_telegram(clean_account)
    
    valid_earnkaro = get_earnkaro_link(clean_account, earnkaro_url, look_id=look_id)
    valid_amazon = get_amazon_link(clean_account, amazon_url) if amazon_url else None
    
    lines = [
        f"✨ {telegram_info['display_name']} — CURATED DROP ✨",
        f"👗 Look: {title}",
        f"🏷️ Price: {price}",
        f"🛍️ Direct Shop Link: {valid_earnkaro}",
    ]
    if valid_amazon:
        lines.append(f"📦 Amazon Alternate: {valid_amazon}")
    lines.append("")
    lines.append("📌 Pinned in channel. Drop comments/questions below.")
    lines.append("Disclosures: Links contain affiliate tracking tags (#affiliate). Curated at zero extra cost to you.")
    return "\n".join(lines)


def get_creator_look_catalog(account: str) -> list[dict[str, Any]]:
    """Returns curated shoppable look catalog for given creator with fully tracked links."""
    clean_account = normalize_account_handle(account)
    raw_looks = CREATOR_LOOK_CATALOG.get(clean_account, [])
    formatted_looks = []
    for look in raw_looks:
        item = dict(look)
        lid = item.get("look_id", "default")
        item["earnkaro_tracked_url"] = get_earnkaro_link(clean_account, item["base_url"], look_id=lid)
        if item.get("amazon_url"):
            item["amazon_tracked_url"] = get_amazon_link(clean_account, item["amazon_url"])
        formatted_looks.append(item)
    return formatted_looks


def validate_all_creator_mappings() -> dict[str, Any]:
    """
    Validates complete configuration and formatting integrity for all 5 creators:
    - Canonical Telegram channel URLs and handles.
    - Amazon Associates tracking tags (-21).
    - EarnKaro sub-ID pattern formatting.
    - Trigger keyword availability.
    - Curated looks catalog integrity.
    """
    report: dict[str, Any] = {"is_valid": True, "creators": {}}
    
    for account in CREATOR_ACCOUNTS:
        creator_status: dict[str, Any] = {"status": "PASS", "checks": {}}
        
        # 1. Telegram Check
        try:
            tg = get_creator_telegram(account)
            tg_valid = tg["url"].startswith("https://t.me/") and tg["handle"].startswith("@")
            creator_status["checks"]["telegram"] = "PASS" if tg_valid else "FAIL"
            if not tg_valid:
                report["is_valid"] = False
        except Exception as e:
            creator_status["checks"]["telegram"] = f"FAIL: {e}"
            report["is_valid"] = False

        # 2. Amazon Tag Check
        try:
            tag = get_amazon_tag(account)
            test_amazon = get_amazon_link(account, "https://www.amazon.in/dp/B08SAMPLE")
            amz_valid = validate_amazon_link(test_amazon, expected_account=account)
            creator_status["checks"]["amazon"] = "PASS" if amz_valid else "FAIL"
            if not amz_valid:
                report["is_valid"] = False
        except Exception as e:
            creator_status["checks"]["amazon"] = f"FAIL: {e}"
            report["is_valid"] = False

        # 3. EarnKaro SubID Check
        try:
            test_ek = get_earnkaro_link(account, "https://topdeal.app.link/sample", look_id="look1")
            ek_valid = validate_earnkaro_link(test_ek, expected_account=account)
            creator_status["checks"]["earnkaro"] = "PASS" if ek_valid else "FAIL"
            if not ek_valid:
                report["is_valid"] = False
        except Exception as e:
            creator_status["checks"]["earnkaro"] = f"FAIL: {e}"
            report["is_valid"] = False

        # 4. Trigger Keywords Check
        kws = get_creator_keywords(account)
        required_core = ["link", "outfit", "fit"]
        kws_valid = all(kw in kws for kw in required_core)
        creator_status["checks"]["keywords"] = "PASS" if kws_valid else "FAIL"
        if not kws_valid:
            report["is_valid"] = False

        # 5. Catalog Check
        catalog = get_creator_look_catalog(account)
        catalog_valid = len(catalog) >= 2
        creator_status["checks"]["catalog"] = "PASS" if catalog_valid else "FAIL"
        if not catalog_valid:
            report["is_valid"] = False

        creator_status["status"] = "PASS" if all(v == "PASS" for v in creator_status["checks"].values()) else "FAIL"
        report["creators"][account] = creator_status

    return report
