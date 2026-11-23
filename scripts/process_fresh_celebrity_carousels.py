"""
process_fresh_celebrity_carousels.py
Automated pipeline to process, watermark-eliminate, format to 4:5 portrait, and stage
the newly generated Google Flow celebrity-inspired carousels:
1. GAGAN: Royal Velvet Bandhgala (Club Library Lounge) - 3 Slides
2. AVANYA: Draped Chocolate Cowl Gown (Brutalist Terrace at Dusk) - 3 Slides
3. MAIRA: Champagne Gold Tissue Silk Saree (Taj Falaknuma Palace) - 3 Slides
"""

import os
import json
import uuid
from datetime import datetime
from prepare_instagram_media import process_image_for_instagram

PROJECT_DIR = r"c:\resrise-studio"
SANDBOX_DOWNLOADS = r"C:\Users\Gagan\.gemini\antigravity\brain\92c329d9-663a-4239-89b1-10cfe0b8e3a9\browser_sandbox\downloads"
DRAFT_DIR = os.path.join(PROJECT_DIR, "draft_media")
QUEUE_PATH = os.path.join(PROJECT_DIR, "swarm_queue.json")
TELEGRAM_QUEUE_PATH = os.path.join(PROJECT_DIR, "telegram_drops_queue.json")

def process_carousels():
    exact_files = {
        "gagan": [
            os.path.join(SANDBOX_DOWNLOADS, "Man_standing_near_bookshelf_71f3af2d_2K.jpg"),
            os.path.join(SANDBOX_DOWNLOADS, "Man_resting_on_leather_armchair_8413e6e8_2K.jpg"),
            os.path.join(SANDBOX_DOWNLOADS, "Man_fastening_velvet_button_98a6da5b_2K.jpg")
        ],
        "avanya": [
            os.path.join(SANDBOX_DOWNLOADS, "Woman_walking_on_wet_terrace_700c5bf8_2K.jpg"),
            os.path.join(SANDBOX_DOWNLOADS, "Woman_turning_head_in_gown_3b4437a3_2K.jpg"),
            os.path.join(SANDBOX_DOWNLOADS, "Close-up_highlighting_chocolate___623af90f_2K.jpg")
        ],
        "maira": [
            os.path.join(SANDBOX_DOWNLOADS, "Woman_walking_through_marble_arches_32a1e2c6_2K.jpg"),
            os.path.join(SANDBOX_DOWNLOADS, "Woman_adjusting_tissue_saree_3d4c6043.jpg"),
            os.path.join(SANDBOX_DOWNLOADS, "Gold_silk_drape_and_pearls_789cb376_2K.jpg")
        ]
    }
    
    staged = {}

    # Gagan
    g_out = []
    for idx, f in enumerate(exact_files["gagan"], start=1):
        target = os.path.join(DRAFT_DIR, "iamgagankumar", f"fresh_velvet_bandhgala_slide{idx}.jpg")
        process_image_for_instagram(f, target)
        g_out.append(target)
        print(f"Staged GAGAN Slide {idx}: {target}")
    staged["gagan"] = g_out

    # Avanya
    a_out = []
    for idx, f in enumerate(exact_files["avanya"], start=1):
        target = os.path.join(DRAFT_DIR, "avanyamehra", f"fresh_chocolate_gown_slide{idx}.jpg")
        process_image_for_instagram(f, target)
        a_out.append(target)
        print(f"Staged AVANYA Slide {idx}: {target}")
    staged["avanya"] = a_out

    # Maira
    m_out = []
    for idx, f in enumerate(exact_files["maira"], start=1):
        target = os.path.join(DRAFT_DIR, "mairamehraofficial", f"fresh_gold_tissue_saree_slide{idx}.jpg")
        process_image_for_instagram(f, target)
        m_out.append(target)
        print(f"Staged MAIRA Slide {idx}: {target}")
    staged["maira"] = m_out

    # Update swarm_queue.json
    update_swarm_queue(staged)
    update_telegram_queue(staged)

    return staged

def update_swarm_queue(staged):
    with open(QUEUE_PATH, "r", encoding="utf-8-sig") as f:
        queue = json.load(f)

    # 1. GAGAN Post
    gagan_post = {
        "id": "fresh_gagan_velvet_bandhgala",
        "account": "iamgagankumar",
        "display_name": "Gagan Kumar",
        "day_index": 16,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Carousel (3 Slides 4:5)",
        "pillar": "Royal Indian Black-Tie: The Velvet Bandhgala Edit",
        "location": "The Heritage Club Lounge, New Delhi, India",
        "viral_score": 99,
        "viral_reason": "Ranveer & SRK inspired bespoke velvet bandhgala with antique silver detailing. Peak wedding cocktail attire demand.",
        "image_prompt": "3-slide editorial carousel of Gagan Kumar in bespoke midnight black royal velvet Bandhgala suit in a luxury club library lounge.",
        "caption": """When bespoke tailoring speaks of royalty and restraint. The midnight velvet Bandhgala edit. 👑✨

Every seam carries understated heritage elegance. Paired with antique silver buttons, silk pocket square, and an understated dress watch for evening black-tie occasions.

Save this look for your winter cocktail & reception wardrobe.
Curated tailoring details & direct sourcing links in bio club ⤵

#GaganKumar #VelvetBandhgala #BespokeMenswear #RoyalBlackTie #WinterWeddings #ResriseStudio #IndianMenswear""",
        "media_paths": staged["gagan"],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-25 12:00 PM",
        "alt_texts": [
            "Slide 1: Full-length portrait of @iamgagankumar standing by dark oak library bookshelves in bespoke midnight black velvet Bandhgala with antique silver buttons.",
            "Slide 2: Medium waist-up portrait of @iamgagankumar seated in charcoal leather Chesterfield armchair, wearing midnight velvet jacket and minimalist dress watch.",
            "Slide 3: Macro close-up detail shot of @iamgagankumar fastening the ornate silver button on the plush velvet bandhgala lapel."
        ]
    }

    # 2. AVANYA Post
    avanya_post = {
        "id": "fresh_avanya_chocolate_gown",
        "account": "avanyamehra",
        "display_name": "Avanya Mehra",
        "day_index": 16,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Carousel (3 Slides 4:5)",
        "pillar": "Quiet Luxury: The Draped Cowl Jersey Edit",
        "location": "Milan, Italy",
        "viral_score": 98,
        "viral_reason": "Hailey Bieber viral Saint Laurent inspired draped chocolate cowl-back jersey gown. High TikTok/Reels save rate.",
        "image_prompt": "3-slide editorial carousel of Avanya Mehra in chocolate brown fluid draped jersey column gown on a rain-washed Milanese terrace at dusk.",
        "caption": """Blue hour reflections in Milan. Fluidity meets sculpture. 🕊️✨

There's an effortless power in fluid jersey tailoring that moves with you. Styled with a molten-gold cuff and understated brutalist architecture.

Save this silhouette for your evening gala moodboard.
Direct dress & jewelry sourcing links in Luxe Vault bio ⤵

#AvanyaMehra #QuietLuxury #ChocolateGown #MilanFashionWeek #EveningElegance #SaintLaurentDupe #ResriseStudio""",
        "media_paths": staged["avanya"],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-25 06:00 AM",
        "alt_texts": [
            "Slide 1: Full-length editorial street portrait of @avanyamehra walking across a rain-washed architectural terrace in a fluid chocolate brown jersey gown at twilight.",
            "Slide 2: Medium 3/4 candid portrait of @avanyamehra turning toward camera with low cowl-back drape and sculptural molten-gold cuff.",
            "Slide 3: Macro close-up on the delicate cowl drape of the chocolate silk jersey fabric and reflective gold cuff detailing."
        ]
    }

    # 3. MAIRA Post
    maira_post = {
        "id": "fresh_maira_gold_tissue_saree",
        "account": "mairamehraofficial",
        "display_name": "Maira Mehra",
        "day_index": 16,
        "status": "APPROVED",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "Carousel (3 Slides 4:5)",
        "pillar": "Royal Heritage Couture: The Gold Metallic Tissue Saree Edit",
        "location": "Taj Falaknuma Palace, Hyderabad, India",
        "viral_score": 99,
        "viral_reason": "Alia Bhatt & Deepika Padukone viral gold tissue silk saree with scalloped border and Kundan choker. #1 trending ethnic search.",
        "image_prompt": "3-slide editorial carousel of Maira Mehra in champagne gold metallic tissue silk saree at Taj Falaknuma Palace corridor.",
        "caption": """Gilded corridors of Falaknuma. When molten gold metallic tissue silk catches the golden hour light. 👑✨

Every fold glows with subtle luminescence. The scalloped antique zari border and multi-tier pearl Kundan choker make this the season's ultimate wedding guest statement.

Save for your festive & bridal moodboard.
Full saree source & jewelry links in bio club ⤵

#MairaMehra #TissueSilkSaree #FalaknumaPalace #GoldTissueSaree #KundanChoker #RoyalWeddingGuest #ResriseStudio""",
        "media_paths": staged["maira"],
        "collaborators": ["resrise"],
        "tagged_users": ["resrise"],
        "scheduled_for": "2026-11-25 09:00 AM",
        "alt_texts": [
            "Slide 1: Regal full-length portrait of @mairamehraofficial walking along the carved marble arches of Taj Falaknuma Palace in a champagne gold tissue silk saree.",
            "Slide 2: Waist-up portrait of @mairamehraofficial gently adjusting the luminous gold tissue pallu and multi-tier pearl Kundan choker.",
            "Slide 3: Macro close-up on the handcrafted scalloped gold zari embroidery, lustrous metallic tissue weave, and Kundan gemstones."
        ]
    }

    # Prepend or replace
    new_posts = [maira_post, avanya_post, gagan_post]
    existing_ids = {p["id"] for p in new_posts}
    queue = [p for p in queue if p.get("id") not in existing_ids]
    queue = new_posts + queue

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)
    print("Updated swarm_queue.json with 3 fresh carousels.")

def update_telegram_queue(staged):
    with open(TELEGRAM_QUEUE_PATH, "r", encoding="utf-8-sig") as f:
        tg_queue = json.load(f)

    fresh_drops = [
        {
            "id": "fresh_maira_gold_tissue_saree",
            "account": "mairamehraofficial",
            "channel": "mairamehraofficial",
            "scheduled_for": "2026-11-25 09:00 AM",
            "drop_text": """👑 **ROYAL WEDDING CURATION: Gilded Champagne Tissue Silk & Kundan**

Featured in today's Taj Falaknuma Palace editorial:
• **Saree**: Handcrafted Metallic Champagne Gold Tissue Silk with Scalloped Zari (₹2,899)
• **Jewelry**: Multi-Strand Faux Pearl Choker with Uncut Kundan Brooch (₹899 | 4.2★ 4,200+ reviews)

🛍️ **Verified Direct Acquisition Links**:
👉 [Amazon Direct Bestseller Tissue Saree](https://www.amazon.in/s?k=metallic+tissue+silk+saree+gold+scalloped+border&tag=gaganresrise-21)
👉 [Amazon Direct Kundan Pearl Choker](https://www.amazon.in/s?k=zaveri+pearls+multi+strand+kundan+choker+set&tag=gaganresrise-21)
👉 [EarnKaro Multi-Store / Myntra Deal](https://topdeal.app.link/maira-tissue-silk?subid=tissue_saree_look)

📌 Pinned in VIP Club. Drop styling questions below!
*Disclosures: Links contain affiliate tracking tags (#affiliate). Curated at zero extra cost to you.*""",
            "image_path": staged["maira"][0]
        },
        {
            "id": "fresh_avanya_chocolate_gown",
            "account": "avanyamehra",
            "channel": "avanyamehra",
            "scheduled_for": "2026-11-25 06:00 AM",
            "drop_text": """✨ **AVANYA MEHRA LUXE VAULT: The Chocolate Jersey Cowl Edit**

Direct high-street & designer dupe sources:
• **Gown**: Fluid Chocolate Brown Asymmetrical Cowl-Back Jersey Column Gown (₹3,490 | Zara / Mango Dupe)
• **Cuff**: Chunky Sculptural Molten-Gold Irregular Cuff Bracelet (₹1,299)

🛍️ **Curated Shopping Links**:
👉 [Amazon Verified Draped Cowl Maxi Dress](https://www.amazon.in/s?k=women+draped+cowl+neck+sleeveless+bodycon+maxi+dress+brown&tag=gaganresrise-21)
👉 [Amazon Sculptural Molten Gold Cuff](https://www.amazon.in/s?k=chunky+gold+cuff+bracelet+irregular+molten+metal&tag=gaganresrise-21)
👉 [EarnKaro Zara/Ajio Luxe Link](https://topdeal.app.link/avanya-brown-dress?subid=avanya_jersey_look)

👉 [Unlock VIP Sources in Luxe Vault](https://t.me/avanyamehra_luxe) #affiliate""",
            "image_path": staged["avanya"][0]
        },
        {
            "id": "fresh_gagan_velvet_bandhgala",
            "account": "iamgagankumar",
            "channel": "iamgagankumar",
            "scheduled_for": "2026-11-25 12:00 PM",
            "drop_text": """⚡ **MEN'S CAPSULE CLUB: Royal Black-Tie Velvet Bandhgala**

Evening Menswear Breakdown:
• **Jacket**: Midnight Black Royal Velvet Bandhgala with Matte Silver Buttons (₹4,799)
• **Timepiece**: Classic Silver-Dial Minimalist Black Leather Dress Watch (₹2,195)
• **Fragrance**: Bella Vita Luxury CEO Man & Date Long-Lasting EDP (₹649 | ASIN: B0DBZTZP67)

🛍️ **Direct Purchase Links**:
👉 [Amazon Velvet Bandhgala Collection](https://www.amazon.in/s?k=men+black+velvet+bandhgala+suit+jacket+wedding&tag=gaganresrise-21)
👉 [Amazon Direct Perfume Deal (ASIN: B0DBZTZP67)](https://www.amazon.in/dp/B0DBZTZP67?tag=gaganresrise-21)
👉 [EarnKaro Myntra Men's Luxe Deal](https://topdeal.app.link/gagan-bandhgala?subid=gagan_velvet_look)

👉 [Access Men's Capsule Community](https://t.me/gagankumar_menswear) #affiliate""",
            "image_path": staged["gagan"][0]
        }
    ]

    existing_tg_ids = {d["id"] for d in fresh_drops}
    tg_queue = [d for d in tg_queue if d.get("id") not in existing_tg_ids]
    tg_queue = fresh_drops + tg_queue

    with open(TELEGRAM_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(tg_queue, f, indent=2, ensure_ascii=False)
    print("Updated telegram_drops_queue.json with 3 fresh drops.")

if __name__ == "__main__":
    res = process_carousels()
    print("Completed staging all fresh carousels:", res)
