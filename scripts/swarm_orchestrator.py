import argparse
import json
import os
import random
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "accounts_config.json")
QUEUE_PATH = os.path.join(PROJECT_DIR, "swarm_queue.json")
DRAFT_MEDIA_DIR = os.path.join(PROJECT_DIR, "draft_media")

OMNIROUTE_URL = os.environ.get("OMNIROUTE_URL", "http://localhost:20128/v1/chat/completions")
OMNIROUTE_MODEL = os.environ.get("OMNIROUTE_MODEL", "gemini/gemini-3-flash-preview")


def load_config() -> dict:
    path = CONFIG_PATH if os.path.exists(CONFIG_PATH) else os.path.join(PROJECT_DIR, "accounts_config.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_queue() -> list:
    if os.path.exists(QUEUE_PATH):
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_queue(queue: list) -> None:
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def find_unassigned_media(account: str, queue: list, max_files: int = 1) -> list:
    """Look in draft_media/<account>/ for 1 or more unassigned images/videos (supports carousels)."""
    account_media_dir = os.path.join(DRAFT_MEDIA_DIR, account)
    os.makedirs(account_media_dir, exist_ok=True)
    used_files = set()
    for item in queue:
        for p in item.get("media_paths", []):
            used_files.add(p)
        if item.get("media_path"):
            used_files.add(item["media_path"])

    valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov")
    found = []
    for fname in sorted(os.listdir(account_media_dir)):
        if fname.lower().endswith(valid_exts):
            full_path = os.path.join(account_media_dir, fname)
            if full_path not in used_files:
                found.append(full_path)
                if len(found) >= max_files:
                    break
    return found


def call_ai_if_available(prompt: str) -> str:
    """Uses local OmniRoute (port 20128) first, then GEMINI_API_KEY fallback."""
    payload = json.dumps({
        "model": OMNIROUTE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(OMNIROUTE_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return ""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return ""


class ConceptAgent:
    """Agent 1: Picks content pillar, location, and post format."""

    @staticmethod
    def run(account: str, profile: dict) -> dict:
        pillar = random.choice(profile["pillars"])
        location = random.choice(profile["locations"])
        post_format = random.choice(["Carousel (3-5 frames)", "Single Portrait (4:5)", "Reel (9:16)"])
        return {
            "pillar": pillar,
            "location": location,
            "format": post_format,
        }


class VisualPromptAgent:
    """Agent 2: Builds raw smartphone-candid realism prompts inspired by @okay.adiiti (no glossy Leica/studio editorial)."""

    @staticmethod
    def run(account: str, profile: dict, concept: dict) -> str:
        is_reel = "reel" in concept.get("format", "").lower()
        if is_reel:
            ai_prompt = (
                f"Write one raw smartphone vertical 9:16 Reel video prompt (max 50 words) for "
                f"{profile['display_name']} (@{account}) in {concept['location']}, theme: {concept['pillar']}. "
                "Include: raw smartphone 9:16 vertical video, 4-6s slow turn or hair-flip motion, "
                "natural direct sunlight or subtle night-time on-camera flash, real skin pores and stray hairs, "
                "candid mid-laugh glance at phone camera, slightly imperfect framing, 35mm warm film tone, no heavy retouching, no watermarks."
            )
            fallback = (
                f"Raw smartphone 9:16 vertical video of {profile['display_name']} (@{account}) in {concept['location']}, "
                f"wearing {concept['pillar']}. 4-6s slow turn and candid hair-flip motion, natural direct sunlight, "
                "real skin pores and stray hairs, mid-laugh glance at phone camera, slightly imperfect framing, 35mm warm film tone, no heavy retouching."
            )
        else:
            ai_prompt = (
                f"Write one raw smartphone-candid photo prompt (max 50 words) for "
                f"{profile['display_name']} (@{account}) in {concept['location']}, theme: {concept['pillar']}. "
                "Include: candid smartphone photo, natural direct sunlight or subtle night-time on-camera flash, "
                "real skin pores and stray hairs, mid-laugh or candid hair-touch pose, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching, no watermarks."
            )
            fallback = (
                f"Candid smartphone photo of {profile['display_name']} (@{account}) in {concept['location']}, "
                f"wearing {concept['pillar']}. Natural direct sunlight or subtle night-time on-camera flash, "
                "real skin pores and stray hairs, mid-laugh or candid hair-touch pose, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching."
            )

        generated = call_ai_if_available(ai_prompt)
        return generated if generated else fallback


class CopywriterAgent:
    """Agent 3: Writes punchy conversational/Hinglish captions (inspired by @okay.adiiti) + 4-5 clean hashtags."""

    CLEAN_HASHTAGS = {
        "avanyamehra": "#AvanyaMehra #QuietLuxury #OOTDInspo #MinimalFit #LuxeVault",
        "mairamehraofficial": "#MairaMehra #SareeDrape #DesiOOTD #WeddingSeason #EthnicVibes",
        "iamgagankumar": "#GaganKumar #MenswearCapsule #LinenFit #MensStyle #DelhiFit",
        "resrise": "#ResriseStudio #CreativeStudio #SetLife #VisualDirection #CreatorSystems",
        "gagankumarrocks": "#GaganKumarRocks #CreatorTech #DeskSetup #FounderMindset #MediaSystems",
    }

    TEMPLATES = {
        "avanyamehra": [
            "Dilli winters & oversized coats just hit different ☕\n\nOutfit details pinned in bio club 🤍",
            "Running 10 mins late as usual 🥐\n\nExact pieces linked in my bio vault ✨",
            "Subtle flex, zero noise 🤎\n\nSaved the full look breakdown in bio ⤵",
            "When the sunlight does 90% of the styling work ☀️\n\nSourcing all pieces in bio vault 🤍",
        ],
        "mairamehraofficial": [
            "Golden hour pe ye drape... no filter needed 🌸✨\n\nExact saree source pinned in my bio club ⤵",
            "Mummy approved this saree in 2 seconds 🌸\n\nGrab the direct piece in bio club ✨",
            "Draping took 5 mins, photos took 50 📸\n\nFull drape details live in bio club 🌸",
            "Udaipur mornings and vintage jhumkas 🤍\n\nJewelry & saree links saved in bio club 🌸",
        ],
        "iamgagankumar": [
            "Linen season rules: keep it simple, keep it sharp ⚡\n\nFit & scent details in bio capsule ⤵",
            "Bandhgala fitting right for tonight's wedding 🖤\n\nDirect suit piece linked in bio club ⚡",
            "Old-school coffee run in rolled sleeves ☕⚡\n\nFull capsule breakdown in bio link ⤵",
            "Clean tailoring always speaks louder than hype 🔥\n\nGrooming & fit specs in bio capsule ⚡",
        ],
        "resrise": [
            "Behind the scenes on our latest campaign 🎬✨\n\nStudio gear & client roster in bio ⤵",
            "Raw frames straight out of camera on set 🌊📸\n\nProduction deck & gear list in bio link ✨",
            "Golden hour lighting test on set 💡✨\n\nJoin our Telegram studio hub via bio ⤵",
            "On set magic with natural bounce light 🌊\n\nCreative production retainers in bio link ⤵",
        ],
        "gagankumarrocks": [
            "Late night desk flow, bina kisi distraction ke 🚀\n\nMic & keyboard specs in bio link ⤵",
            "Zero noise, pure audio test 🎙️🔥\n\nWorkspace tech & mic specs pinned in bio ⤵",
            "Building systems while everyone is scrolling ☕⚡\n\nFull founder blueprint in bio link 🚀",
            "Monitors on, phone on silent 💻⚡\n\nComplete desk architecture in bio link 🚀",
        ],
    }

    @staticmethod
    def run(account: str, profile: dict, concept: dict) -> str:
        clean_tags = CopywriterAgent.CLEAN_HASHTAGS.get(account, profile.get("hashtags", ""))
        ai_prompt = (
            f"Write a super short, punchy Hinglish or conversational Instagram caption (inspired by @okay.adiiti) "
            f"for @{account} ({profile['display_name']}). Topic: {concept['pillar']} in {concept['location']}. "
            "Rule 1: Line 1 must be 1 short punchy line or 1-2 emoji hook (MAX 8-12 WORDS). "
            "Rule 2: Line 2 must be 1 subtle save or bio-club line (e.g. 'outfit details pinned in bio 🤍'). "
            "Rule 3: No long AI paragraphs, no corporate buzzwords. "
            "Output ONLY the 2-line caption text without hashtags."
        )
        caption = call_ai_if_available(ai_prompt)
        if not caption or len(caption.split()) > 25:
            template = random.choice(CopywriterAgent.TEMPLATES.get(account, CopywriterAgent.TEMPLATES["avanyamehra"]))
            caption = template
        return f"{caption}\n\n{clean_tags}"


class ViralScoreAgent:
    """Agent 4: Scores each post 0-100 and auto-optimizes hooks/CTAs if score < 88."""

    @staticmethod
    def score_draft(account: str, profile: dict, concept: dict, caption: str, media_count: int) -> dict:
        ai_prompt = (
            f"Score this Instagram post draft from 0 to 100 for viral/save/share potential on @{account} ({profile['niche']}).\n"
            f"Format: {concept['format']} (attached media files: {media_count})\n"
            f"Pillar: {concept['pillar']} | Location: {concept['location']}\n"
            f"Caption: {caption[:350]}\n\n"
            "Return ONLY valid JSON: {\"score\": <int 0-100>, \"reason\": \"<max 15 words>\"}"
        )
        raw = call_ai_if_available(ai_prompt)
        if raw:
            try:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start != -1 and end > start:
                    parsed = json.loads(raw[start:end])
                    score = max(0, min(100, int(parsed["score"])))
                    reason = str(parsed.get("reason", "")).strip()
                    if reason:
                        return {"viral_score": score, "viral_reason": reason}
            except Exception:
                pass

        score = 72
        reasons = []
        if "Carousel" in concept["format"] or media_count > 1:
            score += 12
            reasons.append("1-outfit 3-location Carousel boosts swipe saves")
        elif "Reel" in concept["format"]:
            score += 14
            reasons.append("Reel format maximizes non-follower reach")
        if any(k in caption for k in ("?", "Save", "Swipe", "Drop", "Which")):
            score += 8
            reasons.append("strong save/comment CTA")
        return {
            "viral_score": min(98, score + random.randint(2, 6)),
            "viral_reason": "; ".join(reasons).capitalize() + ".",
        }

    @staticmethod
    def run(account: str, profile: dict, concept: dict, caption: str, media_count: int) -> dict:
        result = ViralScoreAgent.score_draft(account, profile, concept, caption, media_count)
        if result["viral_score"] >= 88:
            return {**result, "optimized_caption": caption}

        # Auto-rewrite caption with stronger scroll-stop hook + save/swipe CTA
        opt_prompt = (
            f"Rewrite this Instagram caption for @{account} ({profile['niche']}) so it scores 90+ for saves and shares.\n"
            f"Format: {concept['format']} | Pillar: {concept['pillar']} | Location: {concept['location']}\n"
            "Rules: Line 1 = curiosity/relatable hook (max 10 words). Line 2 = short save or swipe-choice CTA (e.g. 'Save this for...' or 'Slide 1 or 3?'). Keep hashtags at the bottom.\n"
            f"Original:\n{caption}"
        )
        improved = call_ai_if_available(opt_prompt)
        if not improved:
            base_body = caption.split("\n\n#")[0].strip()
            improved = f"{base_body}\n\nSave this for your mood board — which frame wins, 1 or 3? ✨\n\n{profile['hashtags']}"

        re_scored = ViralScoreAgent.score_draft(account, profile, concept, improved, media_count)
        final_score = max(result["viral_score"], re_scored["viral_score"])
        return {
            "viral_score": final_score,
            "viral_reason": re_scored["viral_reason"],
            "optimized_caption": improved,
        }


def upgrade_existing_queue() -> None:
    config = load_config()["accounts"]
    queue = load_queue()
    upgraded = 0
    for item in queue:
        if item.get("status") != "PENDING_APPROVAL":
            continue
        account = item.get("account", "")
        if account not in config:
            continue
        profile = config[account]
        if item.get("format") == "Single Portrait (4:5)":
            item["format"] = "Carousel (4:5)"
        concept = {
            "pillar": item.get("pillar", ""),
            "location": item.get("location", ""),
            "format": item.get("format", "Carousel (4:5)"),
        }
        res = ViralScoreAgent.run(account, profile, concept, item.get("caption", ""), len(item.get("media_paths", [])))
        item["caption"] = res["optimized_caption"]
        item["viral_score"] = res["viral_score"]
        item["viral_reason"] = res["viral_reason"]
        upgraded += 1
        print(f"  ↑ {item.get('day_label', item['id'])} (@{account}) -> Viral Score: {item['viral_score']}/100")
    save_queue(queue)
    print(f"\n✅ Upgraded {upgraded} PENDING_APPROVAL draft(s) in {QUEUE_PATH}")


def run_swarm(accounts: list, count_per_account: int, start_date: str = "") -> None:
    config = load_config()["accounts"]
    queue = load_queue()
    created = 0
    base_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()

    for account in accounts:
        profile = config[account]
        pillars = profile["pillars"]
        locations = profile["locations"]
        print(f"\n[Swarm] Running 4 agents for @{account} ({count_per_account} day(s))...")
        for i in range(count_per_account):
            day_num = i + 1
            sched_dt = base_date + timedelta(days=i)
            sched_date = sched_dt.strftime("%Y-%m-%d")
            day_label = f"Day {day_num} ({sched_dt.strftime('%a %b %d')})"

            # Rotate pillars and locations evenly across the 7-day calendar
            concept = {
                "pillar": pillars[i % len(pillars)],
                "location": locations[i % len(locations)],
                "format": "Reel (9:16)" if day_num in (3, 7) else "Carousel (4:5)",
            }
            image_prompt = VisualPromptAgent.run(account, profile, concept)
            caption = CopywriterAgent.run(account, profile, concept)
            max_media = 4 if "Carousel" in concept["format"] else 1
            media_paths = find_unassigned_media(account, queue, max_files=max_media)
            viral = ViralScoreAgent.run(account, profile, concept, caption, len(media_paths))

            draft = {
                "id": str(uuid.uuid4())[:8],
                "account": account,
                "display_name": profile["display_name"],
                "day_index": day_num,
                "scheduled_date": sched_date,
                "day_label": day_label,
                "status": "PENDING_APPROVAL",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "format": concept["format"],
                "pillar": concept["pillar"],
                "location": concept["location"],
                "viral_score": viral["viral_score"],
                "viral_reason": viral["viral_reason"],
                "image_prompt": image_prompt,
                "caption": viral.get("optimized_caption", caption),
                "media_paths": media_paths,
            }
            queue.append(draft)
            created += 1
            media_note = f"{len(media_paths)} file(s)" if media_paths else "No media attached yet"
            print(
                f"  + {day_label} [id:{draft['id']}] | Viral: {draft['viral_score']}/100 "
                f"-> {concept['pillar']} ({media_note})"
            )

    save_queue(queue)
    print(f"\n✅ Swarm complete: {created} new draft(s) scored & added to {QUEUE_PATH}")
    print("Next step: Run 'python scripts\\approval_dashboard.py' to review & approve.")


if __name__ == "__main__":
    config_accounts = list(load_config()["accounts"].keys())
    parser = argparse.ArgumentParser(description="Generate & score Instagram post drafts using the Resrise Swarm agents.")
    parser.add_argument(
        "-a",
        "--account",
        default="all",
        help=f"Account handle ({', '.join(config_accounts)}, or 'all')",
    )
    parser.add_argument(
        "-n",
        "--count",
        "--days",
        dest="count",
        type=int,
        default=7,
        help="Number of days/posts to generate per account (default: 7)",
    )
    parser.add_argument(
        "--start-date",
        default="",
        help="Start date YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--upgrade-existing",
        action="store_true",
        help="Optimize & re-score existing PENDING_APPROVAL drafts in swarm_queue.json",
    )
    args = parser.parse_args()

    if args.upgrade_existing:
        upgrade_existing_queue()
        raise SystemExit(0)

    target = args.account.strip().lstrip("@").lower()
    if target == "all":
        selected_accounts = config_accounts
    elif target in config_accounts:
        selected_accounts = [target]
    else:
        raise SystemExit(f"Invalid account '{args.account}'. Choose from: {', '.join(config_accounts)} or 'all'")

    run_swarm(selected_accounts, args.count, start_date=args.start_date)