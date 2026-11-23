import json
import os
import uuid
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
QUEUE_PATH = os.path.join(PROJECT_DIR, "swarm_queue.json")
TELEGRAM_DROPS_PATH = os.path.join(PROJECT_DIR, "telegram_drops_queue.json")

def generate_id():
    return uuid.uuid4().hex[:8]

NEW_POSTS = [
    # ---------------- 1. MAIRA MEHRA (Organza Floral & Kundan Choker) ----------------
    {
        "id": generate_id(),
        "account": "mairamehraofficial",
        "display_name": "Maira Mehra",
        "day_index": 15,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (3:4)",
        "pillar": "Modern Festive Organza & Antique Kundan Jewelry",
        "location": "City Palace, Udaipur, Rajasthan, India",
        "viral_score": 98,
        "viral_reason": "High-intent wedding guest pastel organza saree + Kundan choker generates massive saves and affiliate conversions.",
        "image_prompt": "Editorial fashion portrait of creator MAIRA in an exquisite pastel blush pink organza saree with scalloped antique gold zari border and antique Kundan choker in Udaipur courtyard, 85mm f/1.4.",
        "caption": (
            "Ethereal mornings in Udaipur. When delicate pastel organza meets timeless scalloped zari craftsmanship. 🌸✨\r\n\r\n"
            "There's something truly magical about hand-embroidered drapes catching the golden hour sun. Paired this with an antique Kundan choker set.\r\n\r\n"
            "Save this drape for upcoming winter weddings.\r\n"
            "Full saree source & styling links in my bio club ⤵\r\n\r\n"
            "#MairaMehra #OrganzaSaree #PastelDrapes #KundanChoker #WeddingGuestStyle #IndianCouture #ResriseStudio"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day15_maira_organza_choker.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 09:00 AM",
        "alt_texts": [
            "Editorial fashion portrait of @mairamehraofficial in a pastel blush pink floral embroidered organza saree with scalloped antique gold zari border and Kundan choker set, 85mm optical portrait lens."
        ],
        "telegram_drop": (
            "💎 **MAIRA MEHRA VIP DROP: Pastel Blush Organza & Kundan Edit**\n\n"
            "As seen in today's Udaipur editorial:\n"
            "• **Saree**: Hand-Embroidered Pastel Blush Organza with Scalloped Zari (₹2,199)\n"
            "• **Jewelry**: Zaveri Pearls Antique Kundan & Pearl Choker Set (₹749 | 4.0★ 3,500+ reviews)\n\n"
            "🛍️ **Verified Direct Acquisition Links**:\n"
            "👉 [Amazon Collection (Live Saree Search)](https://www.amazon.in/s?k=organza+silk+floral+embroidered+saree+with+scalloped+border&tag=gaganresrise-21)\n"
            "👉 [Amazon Direct Kundan Choker](https://www.amazon.in/dp/B07QBCC7NW?tag=gaganresrise-21)\n"
            "👉 [EarnKaro Multi-Store / Myntra Deal](https://topdeal.app.link/maira-organza-saree?subid=maira_saree_look1)\n\n"
            "📌 Pinned in VIP Club. Drop comments/styling questions below!\n"
            "*Disclosures: Links contain affiliate tracking tags (#affiliate). Curated at zero extra cost to you.*"
        )
    },

    # ---------------- 2. MAIRA MEHRA (Royal Emerald Kanjivaram Soft Silk) ----------------
    {
        "id": generate_id(),
        "account": "mairamehraofficial",
        "display_name": "Maira Mehra",
        "day_index": 14,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (3:4)",
        "pillar": "Royal Heritage Couture & Kanjivaram Silk",
        "location": "City Palace, Jaipur, Rajasthan, India",
        "viral_score": 99,
        "viral_reason": "SWORNOF Amazon bestseller soft silk saree with heavy gold zari triggers instant impulse orders.",
        "image_prompt": "Regal portrait of Maira Mehra inside City Palace Jaipur wearing royal emerald green Kanjivaram soft silk saree with heavy authentic gold zari brocade, 85mm f/1.4.",
        "caption": (
            "When heritage speaks in gold zari and pure emerald silk. Captured at City Palace, Jaipur. 👑✨\r\n\r\n"
            "Every fold carries generations of handloom grace. The heavy brocade pallu and traditional temple border make this the ultimate wedding season statement.\r\n\r\n"
            "Save for your bridal & festive moodboard.\r\n"
            "Curated saree source & blouse styling in bio club ⤵\r\n\r\n"
            "#MairaMehra #KanjivaramSilk #RoyalHeritage #EmeraldSaree #GoldZari #WeddingSeason #ResriseStudio"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day14_maira_royal_silk_saree.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-24 09:00 AM",
        "alt_texts": [
            "Regal portrait of @mairamehraofficial in an emerald green Kanjivaram pure soft silk saree with heavy gold zari brocade pallu at City Palace Jaipur, 85mm f/1.4."
        ],
        "telegram_drop": (
            "👑 **ROYAL WEDDING CURATION: Emerald Kanjivaram Soft Silk**\n\n"
            "Featured in today's Jaipur palace editorial:\n"
            "• **Saree**: SWORNOF Royal Emerald Soft Silk with Heavy Gold Zari Pallu (₹3,499)\n"
            "• **Styling**: Regal pleated drape with antique Polki accessories\n\n"
            "🛍️ **Verified Direct Links**:\n"
            "👉 [Amazon Direct Bestseller (ASIN: B0D96G98KY)](https://www.amazon.in/dp/B0D96G98KY?tag=gaganresrise-21)\n"
            "👉 [Amazon Silk Collection Search](https://www.amazon.in/s?k=soft+kanjivaram+silk+saree+rich+gold+zari+pallu+wedding&tag=gaganresrise-21)\n"
            "👉 [EarnKaro Ajio/Myntra Silk Deal](https://topdeal.app.link/maira-kanjivaram-silk?subid=maira_saree_look2)\n\n"
            "✨ *Resrise Studio Curated Edit | @mairamehraclub #affiliate*"
        )
    },

    # ---------------- 3. AVANYA MEHRA (Parisian Tailored Double-Breasted Blazer) ----------------
    {
        "id": generate_id(),
        "account": "avanyamehra",
        "display_name": "Avanya Mehra",
        "day_index": 14,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (3:4)",
        "pillar": "Parisian Minimalist Tailoring & Quiet Luxury",
        "location": "Place Vendôme, Paris, France",
        "viral_score": 97,
        "viral_reason": "High-fashion minimalist tailoring aesthetic delivers strong affiliate conversion among urban Tier-1 professionals.",
        "image_prompt": "Editorial street style portrait of Avanya Mehra at Place Vendôme Paris in an oversized double-breasted charcoal wool blazer, Leica M11 50mm f/1.4.",
        "caption": (
            "Structure, restraint, and the timeless geometry of Paris. 🖤\r\n\r\n"
            "An oversized, double-breasted wool blazer paired with wide-leg tailoring is the ultimate quiet luxury blueprint.\r\n\r\n"
            "Minimalism is never about less — it's about precision.\r\n"
            "Editorial garment sources & luxury dupes in bio ⤵\r\n\r\n"
            "#AvanyaMehra #ParisTailoring #PlaceVendome #QuietLuxury #StructuredBlazer #OldMoneyAesthetic #ResriseStudio"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "avanyamehra", "day14_avanya_paris_blazer.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 06:00 AM",
        "alt_texts": [
            "Editorial street style portrait of @avanyamehra walking past Parisian stone colonnades in an oversized double-breasted charcoal wool blazer, Leica M11 50mm."
        ],
        "telegram_drop": (
            "✨ **AVANYA MEHRA LUXE VAULT: Parisian Tailoring Edit**\n\n"
            "Direct high-street & designer sources:\n"
            "• **Blazer**: Tailored Double-Breasted Charcoal Structured Blazer (₹4,299 | Zara / Mango Dupe)\n"
            "• **Bag**: Minimalist Italian Leather Shoulder Clutch (₹3,990)\n\n"
            "🛍️ **Curated Shopping Links**:\n"
            "👉 [Amazon Verified Tailored Blazer Collection](https://www.amazon.in/s?k=women+double+breasted+oversized+tailored+blazer&tag=gaganresrise-21)\n"
            "👉 [Amazon Leather Clutch Search](https://www.amazon.in/s?k=minimalist+leather+shoulder+clutch+bag+women&tag=gaganresrise-21)\n"
            "👉 [EarnKaro Zara/Ajio Luxe Link](https://topdeal.app.link/avanya-blazer?subid=avanya_luxe_look1)\n\n"
            "👉 [Unlock VIP Sources in Luxe Vault](https://t.me/avanyamehra_luxe) #affiliate"
        )
    },

    # ---------------- 4. IAMGAGANKUMAR (Pure French Linen Camp Collar Shirt) ----------------
    {
        "id": generate_id(),
        "account": "iamgagankumar",
        "display_name": "Gagan Kumar",
        "day_index": 14,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (3:4)",
        "pillar": "Resort Menswear & Niche Grooming",
        "location": "Connaught Place, New Delhi, India",
        "viral_score": 96,
        "viral_reason": "Old-money linen shirt + signature perfume combo converts at high volume with Indian male buyers.",
        "image_prompt": "Editorial portrait of Gagan Kumar in a relaxed sage green pure French linen camp-collar shirt with rolled sleeves in a sunlit courtyard, 50mm f/1.8.",
        "caption": (
            "Old-money resort discipline: French linen, clean cuts, and uncompromised grooming. ⚡\r\n\r\n"
            "A sage green linen shirt with rolled sleeves and tailored trousers is the easiest high-status uniform any man can wear.\r\n\r\n"
            "Capsule menswear breakdown & signature scent links in bio ⤵\r\n\r\n"
            "#GaganKumar #MenswearCapsule #LinenShirt #OldMoneyMen #GroomingEssentials #TailoredStyle #ResriseStudio"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "iamgagankumar", "day14_gagan_linen_shirt.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 12:00 PM",
        "alt_texts": [
            "Editorial menswear portrait of @iamgagankumar in a relaxed sage green pure French linen camp-collar shirt and vintage steel wristwatch, 50mm f/1.8."
        ],
        "telegram_drop": (
            "⚡ **MEN'S CAPSULE CLUB: The French Linen & Signature Scent Blueprint**\n\n"
            "Menswear Essentials Breakdown:\n"
            "• **Shirt**: Pure French Linen Relaxed Camp Collar Shirt (₹2,799 | Sage Green / Ivory)\n"
            "• **Fragrance**: Bella Vita Luxury CEO Man & Date Long-Lasting EDP (₹649 | Amazon Bestseller ASIN: B0DBZTZP67)\n\n"
            "🛍️ **Direct Purchase Links**:\n"
            "👉 [Amazon Linen Shirt Collection](https://www.amazon.in/s?k=pure+linen+camp+collar+long+sleeve+shirt+men&tag=gaganresrise-21)\n"
            "👉 [Amazon Direct Perfume Deal (ASIN: B0DBZTZP67)](https://www.amazon.in/dp/B0DBZTZP67?tag=gaganresrise-21)\n"
            "👉 [EarnKaro Myntra/Ajio Men's Deal](https://topdeal.app.link/gagan-linen-shirt?subid=gagan_mens_look1)\n\n"
            "👉 [Access Men's Capsule Community](https://t.me/gagankumar_menswear) #affiliate"
        )
    },

    # ---------------- 5. GAGANKUMARROCKS (Creator Desk Setup & Dynamic Mic) ----------------
    {
        "id": generate_id(),
        "account": "gagankumarrocks",
        "display_name": "Gagan Kumar",
        "day_index": 1,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (3:4)",
        "pillar": "Creator Media Systems & High-Ticket Tech Setup",
        "location": "Aerocity, New Delhi, India",
        "viral_score": 96,
        "viral_reason": "High-production creator desk aesthetic + high-ticket podcast mic ($70+) triggers high tech commission earnings.",
        "image_prompt": "Editorial creator desk setup featuring Gagan Kumar with a matte black broadcast microphone on a boom arm and 75% mechanical keyboard at twilight, 35mm f/2.0.",
        "caption": (
            "Your workspace is the physical operating system of your mind. 🚀\r\n\r\n"
            "When you're scaling autonomous digital production, tactile tools matter:\r\n"
            "1. Dynamic broadcast audio (USB/XLR cardioid pickup)\r\n"
            "2. Tactile 75% mechanical switches for high-flow writing\r\n"
            "3. Ambient lighting calibrated for deep focus\r\n\r\n"
            "Full studio desk stack & tech specs linked in bio ⤵\r\n\r\n"
            "#GaganKumarRocks #CreatorDesk #DeskSetup #TechEntrepreneur #MediaSystems #PodcastingSetup #Resrise"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "gagankumarrocks", "day01_gagan_creator_desk_setup.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 06:00 PM",
        "alt_texts": [
            "Editorial creator desk setup featuring @gagankumarrocks with a matte black studio broadcast microphone and 75% wireless mechanical keyboard at twilight, 35mm f/2.0."
        ],
        "telegram_drop": (
            "🚀 **MEDIA SYSTEMS DISPATCH #01: The Studio Desk Architecture**\n\n"
            "Creator & Founder Workspace Essentials:\n"
            "• **Audio**: Cardioid Dynamic Studio Podcast Microphone USB/XLR (₹6,499 | Zero Background Noise)\n"
            "• **Keyboard**: 75% Wireless Hot-Swappable Mechanical Keyboard with RGB (₹5,299)\n\n"
            "🛍️ **Direct Acquisition Links**:\n"
            "👉 [Amazon Studio Microphone Collection](https://www.amazon.in/s?k=dynamic+studio+podcast+microphone+usb+xlr+cardioid&tag=gaganresrise-21)\n"
            "👉 [Amazon Mechanical Keyboard Collection](https://www.amazon.in/s?k=wireless+mechanical+keyboard+75+percent+hot+swappable&tag=gaganresrise-21)\n"
            "👉 [EarnKaro Creator Tech Deal](https://topdeal.app.link/gagan-creator-mic?subid=gagan_growth_blueprint1)\n\n"
            "👉 [Read Founder Memo in Media Systems](https://t.me/gagankumar_growth) #affiliate"
        )
    },

    # ---------------- 6. RESRISE (Amalfi Production Campaign & 100W COB Light) ----------------
    {
        "id": generate_id(),
        "account": "resrise",
        "display_name": "Resrise Studio",
        "day_index": 1,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (3:4)",
        "pillar": "Creative Production & Studio Gear",
        "location": "Amalfi Coast, Campania, Italy",
        "viral_score": 99,
        "viral_reason": "High-end Amalfi coastal campaign establishes studio authority and sells high-ticket continuous studio lights.",
        "image_prompt": "Resrise Studio luxury fashion campaign on a Positano cliffside terrace with continuous 100W COB studio video light and softbox, Hasselblad 35mm wide.",
        "caption": (
            "Production Spotlight: Amalfi Campaign Volume I. 🌊✨\r\n\r\n"
            "Where cinematic realism meets autonomous creative direction. Captured on location with high-end continuous COB studio illumination and medium-format optics.\r\n\r\n"
            "Resrise Studio engineers high-converting visual IP, virtual muses, and editorial campaigns for global brands.\r\n\r\n"
            "Explore our client deck & gear breakdown in bio ⤵\r\n"
            "Inquiries: contact.resrise@gmail.com\r\n\r\n"
            "#ResriseStudio #CreativeProduction #VisualCampaign #HighFashion #StudioLighting #AmalfiEditorial #DigitalMuses"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "resrise", "day01_resrise_luxury_production_campaign.jpg")
        ],
        "collaborators": ["avanyamehra"],
        "tagged_users": ["avanyamehra", "gagankumarrocks"],
        "scheduled_for": "2026-11-23 03:00 PM",
        "alt_texts": [
            "Resrise Studio luxury fashion campaign on a Positano cliffside terrace overlooking the Mediterranean sea with professional continuous studio video lighting equipment, 35mm wide."
        ],
        "telegram_drop": (
            "✨ **RESRISE STUDIO VIP ROSTER: Amalfi Campaign Vol. I**\n\n"
            "Production & Lighting Breakdown:\n"
            "• **Gear**: 100W Bi-Color COB Continuous Studio Video Light with Bowens Softbox (₹11,999)\n"
            "• **Optics**: Medium-format 35mm simulation with warm Mediterranean bounce\n"
            "• **Retainers**: Autonomous brand production packages & virtual character licensing\n\n"
            "🛍️ **Direct Studio Gear Links**:\n"
            "👉 [Amazon Verified Studio COB Lighting](https://www.amazon.in/s?k=cob+continuous+video+light+100w+bowens+mount+softbox&tag=gaganresrise-21)\n"
            "👉 [EarnKaro Studio Gear Deal](https://topdeal.app.link/resrise-studio-light?subid=resrise_studio_service1)\n\n"
            "👉 [Join Resrise Studio Hub](https://t.me/resrise_studio) #affiliate"
        )
    }
]

def apply_new_posts():
    # Load existing queue
    queue = []
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8-sig") as f:
            queue = json.load(f)

    # Filter out any non-existent media paths or replace with fresh approved posts at front
    # Set status of previously scheduled posts to STOPPED
    for p in queue:
        if p.get("status") == "APPROVED":
            p["status"] = "STOPPED"

    for p in NEW_POSTS:
        if "media_paths" in p and "media_files" not in p:
            p["media_files"] = p["media_paths"]

    updated_queue = NEW_POSTS + queue
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_queue, f, indent=2, ensure_ascii=False)
    print(f"Successfully added {len(NEW_POSTS)} new APPROVED posts to swarm_queue.json!")

    # Also save telegram drops
    telegram_drops = [
        {
            "id": p["id"],
            "account": p["account"],
            "channel": p["account"],
            "scheduled_for": p["scheduled_for"],
            "drop_text": p["telegram_drop"]
        }
        for p in NEW_POSTS
    ]
    with open(TELEGRAM_DROPS_PATH, "w", encoding="utf-8") as f:
        json.dump(telegram_drops, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(telegram_drops)} Telegram drops to telegram_drops_queue.json!")

if __name__ == "__main__":
    apply_new_posts()
