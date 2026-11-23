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
    # ---------------- 1. MAIRA MEHRA 4-SLIDE MIXED-MEDIA CAROUSEL (Emerald Satin Hotel Suite - 3 Photos + 1 Video Reel) ----------------
    {
        "id": generate_id(),
        "account": "mairamehraofficial",
        "display_name": "Maira Mehra",
        "day_index": 17,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Mixed Carousel (4 slides: 3 photos + 1 video)",
        "pillar": "Liquid Emerald Green Satin Saree & Hotel Bedside Drape (Adiiti Realism)",
        "location": "The Oberoi Grand, Luxury Suite, Kolkata, India",
        "viral_score": 99,
        "viral_reason": (
            "Mixed-media carousel format (Slide 1 candid bedside lean photo + Slide 2 9:16 motion video reel + "
            "Slide 3 backless halter turn photo + Slide 4 bathroom vanity mirror selfie photo). "
            "Delivers the highest engagement & save-rate on Instagram by combining high-retention video dwell time "
            "with viral swipe mechanics."
        ),
        "image_prompt": (
            "4-slide mixed-media luxury hotel suite carousel of Maira Mehra in a liquid emerald green satin silk saree and backless halter choli:\n"
            "Slide 1 (Hero Photo): Candid morning lifestyle photo sitting on edge of crisp white hotel bedding holding iced coffee, warm morning window light.\n"
            "Slide 2 (Omni Video Reel): 4-second vertical 9:16 motion video of Maira on luxury hotel bed holding iced latte, fluid satin drape catching sunlight.\n"
            "Slide 3 (Backless Turn Photo): Over-the-shoulder candid turn revealing deep backless halter cut, warm ambient bedroom lamps, unretouched spine and skin texture.\n"
            "Slide 4 (Mirror Vanity Selfie Photo): Raw bathroom vanity mirror selfie holding smartphone, flash reflection bounce on marble."
        ),
        "caption": (
            "Green flag energy, always 💚🌿\r\n\r\n"
            "Slide 2 video for the drape in motion! Swipe to see the backless cut & mirror check.\r\n"
            "Exact liquid satin saree & halter blouse pinned in bio club ⤵\r\n\r\n"
            "#MairaMehra #SatinSaree #EmeraldGreen #DesiStyle #SareeDrape #MixedMediaCarousel"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide1.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide2.mp4"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide3.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide4.jpg"),
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide1.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide2.mp4"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide3.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day17_maira_emerald_satin_slide4.jpg"),
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 06:00 PM",
        "alt_texts": [
            "Slide 1: Candid morning photo of @mairamehraofficial sitting on a luxury hotel bed in an emerald green satin saree holding iced coffee.",
            "Slide 2: Vertical video clip showing the liquid emerald green satin drape and morning sunlight in motion.",
            "Slide 3: Candid photo from behind showing @mairamehraofficial glancing over shoulder with backless halter choli.",
            "Slide 4: Raw smartphone mirror selfie of @mairamehraofficial in marble bathroom vanity.",
        ],
        "telegram_drop": (
            "💎 **MAIRA MEHRA VIP DROP: Liquid Emerald Satin & Halter Edit**\n\n"
            "As seen in today's 4-slide mixed-media hotel suite drop:\n"
            "• **Saree**: Liquid Emerald Green Satin Silk Saree with Fluid Fall (₹1,999)\n"
            "• **Blouse**: Emerald Satin Backless Halter Crop Top / Choli (₹699)\n\n"
            "🛍️ **Verified Direct Acquisition Links**:\n"
            "👉 [Amazon Saree Search](https://www.amazon.in/s?k=emerald+green+satin+silk+plain+saree&tag=gaganresrise-21)\n"
            "👉 [Amazon Backless Halter Blouse](https://www.amazon.in/s?k=satin+backless+halter+neck+blouse+green&tag=gaganresrise-21)\n"
            "👉 [EarnKaro Multi-Store / Myntra Deal](https://topdeal.app.link/maira-emerald-satin?subid=maira_emerald_look)\n\n"
            "📌 Pinned in VIP Club. Drop comments/styling questions below!\n"
            "*Disclosures: Links contain affiliate tracking tags (#affiliate). Curated at zero extra cost to you.*"
        ),
    },

    # ---------------- 2. MAIRA MEHRA 3-SLIDE CAROUSEL (Festive Gold Tissue Saree - Adiiti Realism) ----------------
    {
        "id": generate_id(),
        "account": "mairamehraofficial",
        "display_name": "Maira Mehra",
        "day_index": 16,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Carousel (3 slides)",
        "pillar": "Festive Gold Metallic Tissue Silk Saree & Backless Choli (Adiiti Realism)",
        "location": "Taj Falaknuma Palace, Hyderabad, India",
        "viral_score": 99,
        "viral_reason": (
            "3-slide same-outfit saree progression (Archetype 1 backless dori turn + "
            "Archetype 2 double-elbows hair pose + Archetype 3 mirror vanity selfie) replicates "
            "@okay.adiiti's highest-converting format, driving massive saves and comments."
        ),
        "image_prompt": (
            "3-slide candid smartphone carousel of Maira Mehra in the same champagne gold metallic tissue silk saree with sweetheart backless choli and delicate tie strings (dori).\n"
            "Slide 1 (Archetype 1: Backless Turn): Candid smartphone photo from behind, turning her head over her shoulder with a playful smirk, revealing deep backless choli fastened with thin silk dori strings and scalloped antique zari pallu over forearm, warm evening lamp lighting, real skin pores and spine contours.\n"
            "Slide 2 (Archetype 2: Double Elbows Up Pose): Both arms raised gathering hair at the nape of the neck, elbows flared high creating hourglass silhouette, direct on-camera smartphone flash edge contrast, mid-laugh candid expression, stray hairs, silver bindi and dangling jhumkas.\n"
            "Slide 3 (Archetype 3: Mirror Vanity Selfie): Raw vanity mirror selfie holding sleek smartphone, flash reflection bounce, rear camera visible, casual relaxed posture looking through phone screen, 35mm film grain, 4:5 vertical unretouched realism."
        ),
        "caption": (
            "Mummy ki saree but make it spicy 🌸✨\r\n\r\n"
            "Swipe to see the back cut & mirror check! Exact saree source & jewelry pinned in bio club ⤵\r\n\r\n"
            "#MairaMehra #SareeDrape #DesiOOTD #WeddingSeason #EthnicVibes"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day16_maira_adiiti_saree_slide1.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day16_maira_adiiti_saree_slide2.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day16_maira_adiiti_saree_slide3.jpg"),
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day16_maira_adiiti_saree_slide1.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day16_maira_adiiti_saree_slide2.jpg"),
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day16_maira_adiiti_saree_slide3.jpg"),
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 09:00 AM",
        "alt_texts": [
            "Slide 1 (Archetype 1): Candid smartphone photo of @mairamehraofficial turning over her shoulder to show backless choli with delicate dori strings in gold tissue silk saree.",
            "Slide 2 (Archetype 2): Candid smartphone photo of @mairamehraofficial with double elbows up tying hair at the nape in gold tissue saree with on-camera flash.",
            "Slide 3 (Archetype 3): Raw mirror vanity selfie of @mairamehraofficial holding phone with flash bounce in gold tissue saree and Kundan choker.",
        ],
        "telegram_drop": (
            "💎 **MAIRA MEHRA VIP DROP: Festive Gold Tissue Silk & Backless Edit**\n\n"
            "As seen in today's 3-slide viral saree drop:\n"
            "• **Saree**: Handcrafted Molten Gold Metallic Tissue Silk with Scalloped Zari Border (₹2,499)\n"
            "• **Jewelry**: Zaveri Pearls Antique Kundan & Pearl Choker Set (₹749 | 4.0★ 3,500+ reviews)\n\n"
            "🛍️ **Verified Direct Acquisition Links**:\n"
            "👉 [Amazon Saree Search](https://www.amazon.in/s?k=tissue+silk+saree+gold+metallic+scalloped+border&tag=gaganresrise-21)\n"
            "👉 [Amazon Direct Kundan Choker](https://www.amazon.in/dp/B07QBCC7NW?tag=gaganresrise-21)\n"
            "👉 [EarnKaro Multi-Store / Myntra Deal](https://topdeal.app.link/maira-organza-saree?subid=maira_saree_look1)\n\n"
            "📌 Pinned in VIP Club. Drop comments/styling questions below!\n"
            "*Disclosures: Links contain affiliate tracking tags (#affiliate). Curated at zero extra cost to you.*"
        ),
    },

    # ---------------- 2. MAIRA MEHRA (Organza Floral & Kundan Choker) ----------------
    {
        "id": generate_id(),
        "account": "mairamehraofficial",
        "display_name": "Maira Mehra",
        "day_index": 15,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (4:5)",
        "pillar": "Modern Festive Organza & Antique Kundan Jewelry",
        "location": "City Palace, Udaipur, Rajasthan, India",
        "viral_score": 98,
        "viral_reason": "High-intent wedding guest pastel organza saree + Kundan choker generates massive saves and affiliate conversions.",
        "image_prompt": "Candid smartphone photo of Maira Mehra in an exquisite pastel blush pink organza saree with scalloped antique gold zari border and antique Kundan choker in Udaipur courtyard. Natural direct sunlight, real skin pores and stray hairs, mid-laugh candid hair-touch pose, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching.",
        "caption": (
            "Draping took 5 mins, photos took 50 🌸✨\r\n\r\n"
            "Exact saree source & choker pinned in my bio club ⤵\r\n\r\n"
            "#MairaMehra #OrganzaSaree #DesiOOTD #WeddingSeason #EthnicVibes"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day15_maira_organza_choker.jpg")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day15_maira_organza_choker.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 09:00 AM",
        "alt_texts": [
            "Candid smartphone photo of @mairamehraofficial in a pastel blush pink organza saree with scalloped gold zari border and Kundan choker set, 4:5 vertical natural light."
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
        "format": "Single Post (4:5)",
        "pillar": "Royal Heritage Couture & Kanjivaram Silk",
        "location": "City Palace, Jaipur, Rajasthan, India",
        "viral_score": 99,
        "viral_reason": "SWORNOF Amazon bestseller soft silk saree with heavy gold zari triggers instant impulse orders.",
        "image_prompt": "Candid smartphone photo of Maira Mehra inside City Palace Jaipur wearing royal emerald green Kanjivaram soft silk saree with heavy authentic gold zari brocade. Natural direct sunlight casting warm shadows, real skin pores and stray hairs, candid mid-laugh glance, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching.",
        "caption": (
            "Mummy approved this saree in 2 seconds 👑🌸\r\n\r\n"
            "Curated silk saree & blouse link in bio club ⤵\r\n\r\n"
            "#MairaMehra #KanjivaramSilk #RoyalHeritage #DesiOOTD #SareeLove"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day14_maira_royal_silk_saree.jpg")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "day14_maira_royal_silk_saree.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-24 09:00 AM",
        "alt_texts": [
            "Candid smartphone portrait of @mairamehraofficial in an emerald green Kanjivaram soft silk saree with heavy gold zari brocade at City Palace Jaipur, 4:5 vertical."
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

    # ---------------- 3. MAIRA MEHRA REEL (Organza Saree 4-6s Slow Turn & Hair-Flip) ----------------
    {
        "id": generate_id(),
        "account": "mairamehraofficial",
        "display_name": "Maira Mehra",
        "day_index": 16,
        "status": "PENDING_APPROVAL",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Reel (9:16)",
        "pillar": "Modern Festive Organza Draping Motion",
        "location": "Udaipur Courtyard, Rajasthan, India",
        "viral_score": 99,
        "viral_reason": "4-6s slow turn motion with natural wind flutter and authentic mid-laugh glance drives high Instagram Reel completion rate.",
        "image_prompt": "Raw smartphone 9:16 vertical video of Maira Mehra in a blush pink organza saree with gold zari border. 4-6s slow turn and gentle hair-flip motion in golden-hour courtyard light, candid laughing glance toward camera, warm lens flare, real skin pores and stray flyaway hairs, natural handheld camera motion, authentic unpolished Instagram Reel realism.",
        "caption": (
            "Golden hour pe ye drape... no filter needed 🌸✨\r\n\r\n"
            "Full saree source & styling links in my bio club ⤵\r\n\r\n"
            "#MairaMehra #SareeReel #DesiVibe #WeddingDrape #SareeLove"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "reel_maira_organza_turn.mp4")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "mairamehraofficial", "reel_maira_organza_turn.mp4")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-25 09:00 AM",
        "alt_texts": [
            "Raw smartphone 9:16 vertical video reel of @mairamehraofficial doing a slow turn and hair-flip in a blush pink organza saree with golden hour sunlight."
        ],
        "telegram_drop": (
            "🌸 **REEL DROP: Pastel Organza Motion Edit**\n\n"
            "Catch the motion in today's reel:\n"
            "• Saree: Hand-Embroidered Pastel Blush Organza with Scalloped Zari (₹2,199)\n"
            "👉 [Amazon Saree Search](https://www.amazon.in/s?k=organza+silk+floral+embroidered+saree+with+scalloped+border&tag=gaganresrise-21)\n"
            "📌 Pinned in VIP Club. #affiliate"
        )
    },

    # ---------------- 4. AVANYA MEHRA (Parisian Tailored Double-Breasted Blazer) ----------------
    {
        "id": generate_id(),
        "account": "avanyamehra",
        "display_name": "Avanya Mehra",
        "day_index": 14,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (4:5)",
        "pillar": "Parisian Minimalist Tailoring & Quiet Luxury",
        "location": "Place Vendôme, Paris, France",
        "viral_score": 97,
        "viral_reason": "High-fashion minimalist tailoring aesthetic delivers strong affiliate conversion among urban Tier-1 professionals.",
        "image_prompt": "Candid smartphone photo of Avanya Mehra at Place Vendôme Paris in an oversized double-breasted charcoal wool blazer. Subtle natural direct sunlight, real skin pores and stray hairs, mid-laugh candid hair-touch pose, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching.",
        "caption": (
            "Running 10 mins late as usual 🥐☕\r\n\r\n"
            "Exact blazer & fit breakdown pinned in bio vault 🤍\r\n\r\n"
            "#AvanyaMehra #ParisOOTD #QuietLuxury #StreetStyle #LuxeVault"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "avanyamehra", "day14_avanya_paris_blazer.jpg")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "avanyamehra", "day14_avanya_paris_blazer.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 06:00 AM",
        "alt_texts": [
            "Candid smartphone street photo of @avanyamehra in an oversized double-breasted charcoal blazer at Place Vendôme Paris, 4:5 vertical."
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

    # ---------------- 5. AVANYA MEHRA REEL (Cowl Dress Parisian Hair-Flip Reel) ----------------
    {
        "id": generate_id(),
        "account": "avanyamehra",
        "display_name": "Avanya Mehra",
        "day_index": 15,
        "status": "PENDING_APPROVAL",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Reel (9:16)",
        "pillar": "Evening Cowl Gowns & Parisian Movement",
        "location": "Pont Alexandre III, Paris, France",
        "viral_score": 98,
        "viral_reason": "4-6s slow turn and hair-flip in golden-hour Parisian breeze generates massive saves and non-follower Discovery.",
        "image_prompt": "Raw smartphone 9:16 vertical video of Avanya Mehra in a draped mocha cowl maxi dress walking through a Parisian street at sunset. 4-6s slow turn and candid hair-flip motion, gentle breeze catching stray hairs, mid-laugh glancing at camera, natural golden hour backlight, subtle handheld smartphone motion, authentic unpolished realism.",
        "caption": (
            "Subtle flex, zero noise 🤎✨\r\n\r\n"
            "Cowl dress & jewelry sources linked in bio vault ⤵\r\n\r\n"
            "#AvanyaMehra #CowlDress #ParisVibes #QuietLuxury #LuxeEdit"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "avanyamehra", "reel_avanya_cowl_flip.mp4")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "avanyamehra", "reel_avanya_cowl_flip.mp4")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-24 06:00 AM",
        "alt_texts": [
            "Raw smartphone 9:16 vertical video reel of @avanyamehra doing a slow turn and hair-flip in a draped mocha cowl maxi dress at sunset."
        ],
        "telegram_drop": (
            "🤎 **AVANYA MEHRA REEL DROP: Cowl Dress Silhouette**\n\n"
            "Featured in today's Parisian sunset reel:\n"
            "👉 [Amazon Cowl Dress Search](https://www.amazon.in/s?k=women+draped+cowl+neck+sleeveless+bodycon+maxi+dress+brown&tag=gaganresrise-21)\n"
            "👉 [VIP Luxe Vault](https://t.me/avanyamehra_luxe) #affiliate"
        )
    },

    # ---------------- 6. IAMGAGANKUMAR (Pure French Linen Camp Collar Shirt) ----------------
    {
        "id": generate_id(),
        "account": "iamgagankumar",
        "display_name": "Gagan Kumar",
        "day_index": 14,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (4:5)",
        "pillar": "Resort Menswear & Niche Grooming",
        "location": "Connaught Place, New Delhi, India",
        "viral_score": 96,
        "viral_reason": "Old-money linen shirt + signature perfume combo converts at high volume with Indian male buyers.",
        "image_prompt": "Candid smartphone photo of Gagan Kumar in a relaxed sage green pure French linen camp-collar shirt with rolled sleeves in a sunlit courtyard. Natural direct sunlight, real skin pores and stray hairs, candid mid-laugh wrist-check pose, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching.",
        "caption": (
            "Linen season rules: keep it simple, keep it sharp ⚡\r\n\r\n"
            "Capsule fit & signature scent details in bio capsule ⤵\r\n\r\n"
            "#GaganKumar #MenswearCapsule #LinenFit #MensStyle #DelhiFit"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "iamgagankumar", "day14_gagan_linen_shirt.jpg")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "iamgagankumar", "day14_gagan_linen_shirt.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 12:00 PM",
        "alt_texts": [
            "Candid smartphone menswear photo of @iamgagankumar in a relaxed sage green French linen shirt, 4:5 vertical natural light."
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

    # ---------------- 7. IAMGAGANKUMAR REEL (Black Velvet Bandhgala Motion Reel) ----------------
    {
        "id": generate_id(),
        "account": "iamgagankumar",
        "display_name": "Gagan Kumar",
        "day_index": 15,
        "status": "PENDING_APPROVAL",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Reel (9:16)",
        "pillar": "Modern Heritage Menswear & Evening Tailoring",
        "location": "Heritage Haveli, New Delhi, India",
        "viral_score": 98,
        "viral_reason": "4-6s slow turn motion adjusting cuff in tailored velvet bandhgala creates high aspirational engagement for festive season.",
        "image_prompt": "Raw smartphone 9:16 vertical video of Gagan Kumar in a black tailored velvet bandhgala suit jacket outside a heritage wedding venue at night. Subtle night-time on-camera flash, 4-6s slow turn adjusting cuff and candid half-smile toward camera, natural grain and real skin texture, handheld phone movement, authentic Instagram Reel realism.",
        "caption": (
            "Bandhgala fitting right for tonight's wedding 🖤⚡\r\n\r\n"
            "Direct bandhgala & scent links in bio capsule ⤵\r\n\r\n"
            "#GaganKumar #Bandhgala #DesiMenswear #WeddingFit #MensStyle"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "iamgagankumar", "reel_gagan_bandhgala_turn.mp4")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "iamgagankumar", "reel_gagan_bandhgala_turn.mp4")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-24 12:00 PM",
        "alt_texts": [
            "Raw smartphone 9:16 vertical video reel of @iamgagankumar adjusting cuffs in a black tailored velvet bandhgala at night."
        ],
        "telegram_drop": (
            "🖤 **REEL DROP: Black Velvet Bandhgala Edit**\n\n"
            "Featured in tonight's wedding fit reel:\n"
            "👉 [Amazon Bandhgala Collection](https://www.amazon.in/s?k=men+black+velvet+bandhgala+suit+jacket+wedding&tag=gaganresrise-21)\n"
            "👉 [Men's Capsule Community](https://t.me/gagankumar_menswear) #affiliate"
        )
    },

    # ---------------- 8. GAGANKUMARROCKS (Creator Desk Setup & Dynamic Mic) ----------------
    {
        "id": generate_id(),
        "account": "gagankumarrocks",
        "display_name": "Gagan Kumar",
        "day_index": 1,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (4:5)",
        "pillar": "Creator Media Systems & High-Ticket Tech Setup",
        "location": "Aerocity, New Delhi, India",
        "viral_score": 96,
        "viral_reason": "High-production creator desk aesthetic + high-ticket podcast mic ($70+) triggers high tech commission earnings.",
        "image_prompt": "Candid smartphone photo of Gagan Kumar at his creator workstation with matte black broadcast mic and 75% mechanical keyboard at twilight. Natural ambient desk lighting and subtle on-camera fill, real skin pores and stray hairs, mid-laugh candid pose adjusting headphones, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching.",
        "caption": (
            "Late night desk flow, bina kisi distraction ke 🚀\r\n\r\n"
            "Full studio desk stack & tech specs in bio link ⤵\r\n\r\n"
            "#GaganKumarRocks #CreatorDesk #DeskSetup #TechSetup #MediaSystems"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "gagankumarrocks", "day01_gagan_creator_desk_setup.jpg")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "gagankumarrocks", "day01_gagan_creator_desk_setup.jpg")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-23 06:00 PM",
        "alt_texts": [
            "Candid smartphone photo of @gagankumarrocks at his creator workstation with a broadcast mic and keyboard at twilight, 4:5 vertical."
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

    # ---------------- 9. GAGANKUMARROCKS REEL (Workstation Audio & Setup Motion Reel) ----------------
    {
        "id": generate_id(),
        "account": "gagankumarrocks",
        "display_name": "Gagan Kumar",
        "day_index": 2,
        "status": "PENDING_APPROVAL",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Reel (9:16)",
        "pillar": "Autonomous Creator Systems & Studio Audio Test",
        "location": "Aerocity Studio, New Delhi, India",
        "viral_score": 97,
        "viral_reason": "4-6s slow turn pulling podcast mic close with RGB twilight desk ambient glow sparks high tech desk curiosity.",
        "image_prompt": "Raw smartphone 9:16 vertical video of Gagan Kumar at his creator desk pulling the broadcast boom mic closer. 4-6s slow turn and candid nod to the beat, ambient RGB twilight glow, real skin pores and unstyled hair, handheld smartphone shake, raw authentic build-in-public Reel realism.",
        "caption": (
            "Zero noise, pure audio test 🎙️🔥\r\n\r\n"
            "Workspace tech & mic specs pinned in bio ⤵\r\n\r\n"
            "#GaganKumarRocks #PodcastSetup #DeskTour #CreatorTech #Workstation"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "gagankumarrocks", "reel_gagan_audio_check.mp4")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "gagankumarrocks", "reel_gagan_audio_check.mp4")
        ],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-24 06:00 PM",
        "alt_texts": [
            "Raw smartphone 9:16 vertical video reel of @gagankumarrocks pulling a broadcast boom mic closer at his desk."
        ],
        "telegram_drop": (
            "🎙️ **TECH REEL DROP: Studio Broadcast Audio**\n\n"
            "Direct links for today's mic test:\n"
            "👉 [Amazon Studio Mic](https://www.amazon.in/s?k=dynamic+studio+podcast+microphone+usb+xlr+cardioid&tag=gaganresrise-21)\n"
            "👉 [Media Systems Community](https://t.me/gagankumar_growth) #affiliate"
        )
    },

    # ---------------- 10. RESRISE (Amalfi Production Campaign & 100W COB Light) ----------------
    {
        "id": generate_id(),
        "account": "resrise",
        "display_name": "Resrise Studio",
        "day_index": 1,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Single Post (4:5)",
        "pillar": "Creative Production & Studio Gear",
        "location": "Amalfi Coast, Campania, Italy",
        "viral_score": 99,
        "viral_reason": "High-end Amalfi coastal campaign establishes studio authority and sells high-ticket continuous studio lights.",
        "image_prompt": "Candid smartphone photo of Resrise Studio production team setting up on a Positano cliffside terrace with continuous 100W COB video light and softbox overlooking the sea. Natural direct sunlight, real skin pores and stray hairs, candid mid-laugh pose adjusting light reflector, slightly imperfect framing, 4:5 vertical, 35mm warm film tone, no heavy retouching.",
        "caption": (
            "Raw frames straight out of camera on set 🌊📸\r\n\r\n"
            "Client production deck & gear specs in bio link ⤵\r\n\r\n"
            "#ResriseStudio #SetLife #CreativeStudio #StudioGear #CreatorAgency"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "resrise", "day01_resrise_luxury_production_campaign.jpg")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "resrise", "day01_resrise_luxury_production_campaign.jpg")
        ],
        "collaborators": ["avanyamehra"],
        "tagged_users": ["avanyamehra", "gagankumarrocks"],
        "scheduled_for": "2026-11-23 03:00 PM",
        "alt_texts": [
            "Candid smartphone photo of @resrise production team adjusting a continuous video light on a Positano cliff terrace, 4:5 vertical."
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
    },

    # ---------------- 11. RESRISE REEL (Positano Sunset Production Wrap Reel) ----------------
    {
        "id": generate_id(),
        "account": "resrise",
        "display_name": "Resrise Studio",
        "day_index": 2,
        "status": "PENDING_APPROVAL",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Reel (9:16)",
        "pillar": "Autonomous Studio Production BTS",
        "location": "Positano Cliffside Terrace, Italy",
        "viral_score": 98,
        "viral_reason": "4-6s slow turn panning across Positano golden hour cliffside to sunset ocean horizon captivates creator audiences.",
        "image_prompt": "Raw smartphone 9:16 vertical video on Positano cliffside terrace during production wrap. 4-6s slow turn panning from continuous COB light to sunset ocean horizon, candid crew laughter, natural golden-hour lens flare, handheld smartphone motion, authentic behind-the-scenes Reel aesthetic.",
        "caption": (
            "Golden hour lighting test on set 🎬✨\r\n\r\n"
            "Studio gear list & client retainers in bio link ⤵\r\n\r\n"
            "#ResriseStudio #BehindTheScenes #VisualProduction #ProductionGear #CreatorAgency"
        ),
        "media_paths": [
            os.path.join(PROJECT_DIR, "draft_media", "resrise", "reel_resrise_amalfi_bts.mp4")
        ],
        "media_files": [
            os.path.join(PROJECT_DIR, "draft_media", "resrise", "reel_resrise_amalfi_bts.mp4")
        ],
        "collaborators": ["avanyamehra"],
        "tagged_users": ["avanyamehra", "gagankumarrocks"],
        "scheduled_for": "2026-11-24 03:00 PM",
        "alt_texts": [
            "Raw smartphone 9:16 vertical video reel of @resrise production set on a Positano cliff overlooking the sea at sunset."
        ],
        "telegram_drop": (
            "🎬 **REEL DROP: Behind The Scenes on Set**\n\n"
            "Lighting & production specs from today's Amalfi reel:\n"
            "👉 [Amazon COB Continuous Light](https://www.amazon.in/s?k=cob+continuous+video+light+100w+bowens+mount+softbox&tag=gaganresrise-21)\n"
            "👉 [Resrise Studio Community](https://t.me/resrise_studio) #affiliate"
        )
    }
]

def apply_new_posts():
    # Load existing queue
    queue = []
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8-sig") as f:
            queue = json.load(f)

    # Deduplicate against previous runs of NEW_POSTS by pillar
    seen_pillars = {p.get("pillar") for p in NEW_POSTS}
    clean_queue = [p for p in queue if p.get("pillar") not in seen_pillars]

    # Set status of previously scheduled/approved posts to STOPPED
    for p in clean_queue:
        if p.get("status") == "APPROVED":
            p["status"] = "STOPPED"

    for p in NEW_POSTS:
        if "media_paths" in p and "media_files" not in p:
            p["media_files"] = p["media_paths"]

    updated_queue = NEW_POSTS + clean_queue
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_queue, f, indent=2, ensure_ascii=False)
    print(f"Successfully added {len(NEW_POSTS)} new posts to swarm_queue.json!")

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
