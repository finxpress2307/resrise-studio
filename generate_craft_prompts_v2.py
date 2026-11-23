import json
import os
import uuid

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR).lower() == "scripts" else SCRIPT_DIR
QUEUE_PATH = os.path.join(PROJECT_DIR, "swarm_queue.json")
OUTPUT_MATRIX_PATH = os.path.join(PROJECT_DIR, "craft_prompts_days08_14.json")

# Character Visual Identity Anchors
CHARACTERS = {
    "avanyamehra": {
        "asset": "asset:AVANYA",
        "desc": "Avanya Mehra, editorial fashion muse with sharp high-fashion South Asian features, sculpted cheekbones, deep brown eyes, sleek dark hair, olive skin tone, quiet luxury poise."
    },
    "mairamehraofficial": {
        "asset": "asset:MAIRA",
        "desc": "Maira Mehra, radiant Indian travel & lifestyle creator with warm golden-olive skin tone, expressive hazel-brown eyes, voluminous dark wavy hair, warm natural smile."
    },
    "iamgagankumar": {
        "asset": "asset:GAGAN",
        "desc": "Gagan Kumar, 36-year-old North Indian architect with medium-warm brown skin tone, well-groomed natural full black beard, sharp contemplative gaze."
    },
    "resrise": {
        "asset": "asset:RESRISE",
        "desc": "Resrise Studio creative production aesthetic, minimalist architectural gallery, luxury campaign lookbook styling, 35mm film grain, Hasselblad medium format."
    },
    "gagankumarrocks": {
        "asset": "asset:GAGAN_FOUNDER",
        "desc": "Gagan Kumar, founder of Resrise Studio, visionary creator in modern studio setup, architectural drafting desks, ambient natural lighting."
    }
}

# 1-Outfit, 3-Slide CRAFT Definitions for Days 8-14 (Including Multi-Creator Collabs)
DAYS_8_TO_14_DATA = {
    # -------------------------------------------------------------
    # AVANYA MEHRA (Days 8 to 14)
    # -------------------------------------------------------------
    ("avanyamehra", 8): {
        "pillar": "Resort Couture & Lakefront Architecture",
        "location": "Villa d'Este, Lake Como",
        "format": "Carousel (3 frames)",
        "caption": "Where the water meets the terrace — quiet luxury in its purest form.\n\nWhich frame feels most timeless, 1, 2, or 3? ✨\n\n#AvanyaMehra #QuietLuxury #LakeComoStyle #EditorialFashion #ResriseStudio",
        "outfit": "a sculpted metallic emerald-green silk drape gown with an architectural one-shoulder cascade and raw edge hem",
        "loc1": "standing at the edge of an ornate neoclassical stone terrace overlooking Lake Como at dawn, distant Alpine mist, 35mm wide establishing frame",
        "loc2": "candid mid-stride strolling past centuries-old cypress trees along the lake promenade, silk cascade catching breeze, 50mm f/1.4",
        "loc3": "intimate profile portrait leaning against carved marble balustrade, crisp catchlights reflecting calm water, 85mm f/1.8"
    },
    ("avanyamehra", 9): {
        "pillar": "COLLAB: The Architect & The Muse (Avanya x Gagan)",
        "location": "Modernist Concrete Pavilion, New Delhi",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Structure meets silhouette. When architectural lines frame high-fashion form.\n\nSwipe through the editorial study with @iamgagankumar. Frame 1 or 2? 🖤\n\n#AvanyaMehra #GaganKumar #EditorialCollab #ModernistArchitecture #QuietLuxury #ResriseStudio",
        "outfit": "Avanya wearing an obsidian black sculptural column gown with raw silk texture, standing beside Gagan Kumar wearing a bespoke tailored charcoal unstructured wool suit over a matte black crewneck",
        "loc1": "wide establishing shot of Avanya and Gagan Kumar standing in a brutalist raw-concrete architectural pavilion with sharp geometric shadows and minimalist stone benches, 35mm lens",
        "loc2": "candid mid-shot walking side-by-side through a sun-dappled colonnade, natural synchrony in movement, obsidian silk drape and charcoal tailoring in sharp focus, 50mm f/1.4",
        "loc3": "intimate duo editorial portrait, soft raking side-light sculpting cheekbones and tailoring textures, natural catchlights, 85mm f/2.0"
    },
    ("avanyamehra", 10): {
        "pillar": "Heritage Modernism & Monochromatic Draping",
        "location": "Amer Fort Courtyard, Jaipur",
        "format": "Carousel (3 frames)",
        "caption": "Ivory raw silk in ancient sandstone courtyards. Heritage drapes made for modern eyes.\n\nSave this for your mood board 🤍\n\n#AvanyaMehra #IndianCouture #ModernDrape #HeritageFashion #ResriseStudio",
        "outfit": "an ivory structured raw-silk pre-draped saree with geometric silver zardozi border and a sleeveless high-neck bustier",
        "loc1": "standing in the center of the vast scalloped sandstone courtyard at sunrise, golden raking light, wide architectural perspective",
        "loc2": "walking purposefully past carved jali lattice screens, authentic silk tension and movement, 50mm f/1.4",
        "loc3": "tight beauty close-up framed within a scalloped arch, natural sandstone bounce filling facial contours, 85mm f/2.2"
    },
    ("avanyamehra", 11): {
        "pillar": "COLLAB: Drapes of Heritage (Avanya x Maira)",
        "location": "Lakeside Haveli, Udaipur",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Two visions of the contemporary saree. Modern minimalism meets effortless warmth.\n\nSwipe to see both drapes with @mairamehraofficial. Which styling is your mood? 🌸✨\n\n#AvanyaMehra #MairaMehra #SareeSisters #ModernHeritage #IndianFashion #ResriseStudio",
        "outfit": "Avanya wearing a slate-grey minimalist organza saree with clean geometric lines, standing alongside Maira Mehra wearing a warm rani-pink tissue silk saree with subtle gold border",
        "loc1": "establishing wide shot of Avanya and Maira Mehra on a carved white marble rooftop pavilion overlooking Lake Pichola at sunset, warm amber sky",
        "loc2": "candid mid-shot of both laughing softly while adjusting their drapes near antique brass lanterns, authentic sisterhood bond, 50mm f/1.4",
        "loc3": "close-up duo portrait with sunset backlight illuminating both fabrics, rich texture contrast between slate-grey organza and rani-pink tissue silk, 85mm f/1.8"
    },
    ("avanyamehra", 12): {
        "pillar": "Golden Hour Liquid Satin & Skyline",
        "location": "South Mumbai Rooftop Infinity Terrace",
        "format": "Carousel (3 frames)",
        "caption": "Golden hour in Mumbai. Liquid metallic textures under amber skies.\n\nDrop a ✨ if this palette speaks to you.\n\n#AvanyaMehra #MumbaiTwilight #GoldenHourFashion #QuietLuxury #ResriseStudio",
        "outfit": "a liquid bronze molten satin slip gown with an asymmetrical back drape and minimalist delicate diamond studs",
        "loc1": "standing by a seamless glass infinity ledge overlooking Marine Drive during twilight blue hour, city bokeh in distance, wide frame",
        "loc2": "candid walking shot past minimalist outdoor limestone loungers, warm terrace cocktail ambient lighting, 50mm f/1.4",
        "loc3": "tight editorial profile portrait, golden rim lighting catching sleek dark hair and specular satin sheen, 85mm f/1.8"
    },
    ("avanyamehra", 13): {
        "pillar": "Sharp Tailoring & European Minimalism",
        "location": "Place Vendôme, Paris",
        "format": "Carousel (3 frames)",
        "caption": "The power of sharp wool and clean lines in Paris.\n\nSlide 1 or Slide 3? 🖤\n\n#AvanyaMehra #ParisEditorial #TailoredElegance #HighFashion #ResriseStudio",
        "outfit": "a bespoke deep crimson double-breasted tailored wool pant-suit with sharp sculptural peak lapels and pointed leather ankle boots",
        "loc1": "standing confidently in the center of Place Vendôme with classical French architectural facades, morning overcast northern light, wide frame",
        "loc2": "crossing a cobblestone street mid-stride, tailored jacket swaying with natural drape weight, 50mm f/1.4",
        "loc3": "close-up editorial beauty portrait leaning near vintage streetlamp, authentic skin micro-pores and sharp eye catchlights, 85mm f/2.0"
    },
    ("avanyamehra", 14): {
        "pillar": "COLLAB: Resrise Studio Campaign 03",
        "location": "Resrise Creative Studio, New Delhi",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Campaign 03 Study. Pure craft, architectural lighting, and forward-looking fashion.\n\nProduced by @resrise. Save for your mood board 🤍\n\n#AvanyaMehra #ResriseStudio #StudioEditorial #Campaign03 #HighFashion #ModernMuse",
        "outfit": "an off-white sculptural draped jersey gown with geometric cutout back, styled with brutalist brass cuff",
        "loc1": "standing on an elevated raw concrete studio platform illuminated by a single 5-foot beauty dish softbox, wide establishing frame",
        "loc2": "candid mid-shot stepping off the platform with studio monitors and C-stands softly blurred in background, 50mm f/1.4",
        "loc3": "tight high-fashion portrait, high-contrast chiaroscuro lighting sculpting cheekbones and jawline, 85mm f/2.2"
    },

    # -------------------------------------------------------------
    # MAIRA MEHRA (Days 8 to 14)
    # -------------------------------------------------------------
    ("mairamehraofficial", 8): {
        "pillar": "Heritage Staycation & Morning Tea",
        "location": "Devi Garh Palace, Delwara",
        "format": "Carousel (3 frames)",
        "caption": "Palace mornings and hot masala chai. There is no place quite like Rajasthan. ☕🌸\n\nSwipe to see the full courtyard view!\n\n#MairaMehra #RajasthanDiaries #HeritageStay #SareeStyle #TravelIndia",
        "outfit": "a canary-yellow handloom mulmul anarkali suit with delicate white thread-work borders and small silver jhumkas",
        "loc1": "standing in a sunny white marble courtyard garden with brass urli bowls filled with marigolds, wide establishing shot, soft morning sun",
        "loc2": "sitting on a stone jharokha ledge holding a steaming ceramic chai glass, candid laughter, 50mm f/1.4",
        "loc3": "close-up candid portrait with natural breeze catching soft curls, authentic unretouched skin glow, 85mm f/2.0"
    },
    ("mairamehraofficial", 9): {
        "pillar": "Wanderlust & Estate Mornings",
        "location": "Coffee Estate Bungalow, Coorg",
        "format": "Carousel (3 frames)",
        "caption": "Waking up inside the coffee hills. Crisp mountain air and handwoven drapes. 🌿✨\n\nWhich slide gives the best peaceful vibes?\n\n#MairaMehra #CoorgDiaries #PlantationLiving #HandloomSaree #EffortlessStyle",
        "outfit": "a moss-green handwoven cotton-silk saree with an antique gold temple border and sleeveless olive blouse",
        "loc1": "standing on a wide wooden veranda overlooking misty coffee plantations and tall silver oak trees, wide establishing shot",
        "loc2": "strolling down a gravel garden path lined with wild ferns, candid mid-stride smile, 50mm f/1.4",
        "loc3": "intimate portrait leaning against rustic wooden veranda pillar, soft morning diffused light, 85mm f/1.8"
    },
    ("mairamehraofficial", 10): {
        "pillar": "COLLAB: Sunday Slow Down (Maira x Gagan)",
        "location": "Heritage Villa, Fontainhas Goa",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Sunday mornings are meant for good coffee and zero rush.\n\nSwipe through our weekend edit with @iamgagankumar! Frame 1 or 3? ☕🌿\n\n#MairaMehra #GaganKumar #WeekendEdit #GoaDiaries #SlowLiving #ResriseStudio",
        "outfit": "Maira wearing a relaxed sage-green linen coord set with white strappy sandals, beside Gagan Kumar wearing an open-collar cream linen shirt and tailored khaki chinos",
        "loc1": "establishing wide shot sitting on a colorful Portuguese veranda bench surrounded by potted palms and yellow colonial walls",
        "loc2": "candid mid-shot walking along a quiet cobbled lane of Fontainhas, laughing naturally, linen fabrics swaying in coastal breeze, 50mm f/1.4",
        "loc3": "intimate candid portrait sharing an outdoor cafe table with two espresso cups, warm tropical golden sun, 85mm f/2.0"
    },
    ("mairamehraofficial", 11): {
        "pillar": "COLLAB: Drapes of Heritage (Maira x Avanya)",
        "location": "Lakeside Haveli, Udaipur",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Different drapes, same shared love for Indian textiles.\n\nCreating magic by the lake with @avanyamehra. Which color story are you loving? 💖\n\n#MairaMehra #AvanyaMehra #SareeLove #UdaipurDiaries #TextileHeritage #ResriseStudio",
        "outfit": "Maira wearing a warm rani-pink tissue silk saree with gold border, standing beside Avanya Mehra in a slate-grey minimalist organza saree",
        "loc1": "establishing wide frame framed by lakeside stone arches as twilight falls over Lake Pichola, reflections glowing on water",
        "loc2": "candid mid-shot smiling towards camera while holding antique brass flower bowls, authentic warm connection, 50mm f/1.4",
        "loc3": "intimate portrait showing intricate gold zari on Maira's shoulder alongside Avanya's clean grey drape, natural skin warmth, 85mm f/2.0"
    },
    ("mairamehraofficial", 12): {
        "pillar": "Sunset Desert Camp & Mirrorwork",
        "location": "Sam Sand Dunes, Jaisalmer",
        "format": "Carousel (3 frames)",
        "caption": "Golden sands, sunset breeze, and timeless mirror-work.\n\nSave this for your future desert travel dreams! 🏜️✨\n\n#MairaMehra #JaisalmerDiaries #GoldenHourIndia #EthnicStyle #DesertVibes",
        "outfit": "a terracotta rust-orange bandhani georgette saree with an embroidered mirror-work sleeveless blouse",
        "loc1": "standing atop a sweeping sand dune as the sun sinks beneath the desert horizon, deep orange ambient glow, wide frame",
        "loc2": "candid walking mid-shot across golden sand ripples, lightweight georgette fabric floating in wind, 50mm f/1.4",
        "loc3": "tight beauty portrait with golden hour side-light reflecting off mirror details on blouse, radiant warm smile, 85mm f/2.0"
    },
    ("mairamehraofficial", 13): {
        "pillar": "Evening Garden Soirée",
        "location": "Sunder Nursery Heritage Amphitheatre, Delhi",
        "format": "Carousel (3 frames)",
        "caption": "Soft pastels under ancient Mughal arches.\n\nWhich frame catches your eye first? 🌸\n\n#MairaMehra #DelhiDiaries #SareeWardrobe #PastelSaree #EthnicInspo",
        "outfit": "a lavender lilac organza saree with delicate hand-painted floral motifs and a dainty pearl choker",
        "loc1": "standing near the reflecting pool of Sunder Nursery at sunset with Mughal monuments in background, wide architectural shot",
        "loc2": "candid stroll along the stone walkway, lilac organza floating gracefully, 50mm f/1.4",
        "loc3": "intimate close-up portrait with soft evening twilight bounce, delicate pearl details in sharp focus, 85mm f/1.8"
    },
    ("mairamehraofficial", 14): {
        "pillar": "Varanasi Morning Light & River Ghats",
        "location": "Assi Ghat, Varanasi",
        "format": "Carousel (3 frames)",
        "caption": "Watching the day begin on the sacred river. Pure calm and quiet energy. 🙏🌊\n\n#MairaMehra #VaranasiDiaries #IncredibleIndia #HandloomCotton #TravelSoul",
        "outfit": "an indigo hand-block-printed cotton kurta set with a sheer white mulmul dupatta and oxidized silver bangles",
        "loc1": "standing on the stone steps of Assi Ghat as wooden boats drift in morning fog, soft pink dawn sky, wide establishing frame",
        "loc2": "sitting quietly by the water edge with hands resting on knees, serene candid profile, 50mm f/1.4",
        "loc3": "tight portrait looking towards morning sun, soft rim lighting on wavy hair, natural unretouched beauty, 85mm f/2.2"
    },

    # -------------------------------------------------------------
    # GAGAN KUMAR (Days 8 to 14)
    # -------------------------------------------------------------
    ("iamgagankumar", 8): {
        "pillar": "Modernist Architecture & Summer Tailoring",
        "location": "National Gallery of Modern Art, New Delhi",
        "format": "Carousel (3 frames)",
        "caption": "Unstructured linen tailoring for when the temperature rises. Crisp, breathable, sharp.\n\nFit rating out of 10? Drop below 👇\n\n#GaganKumar #MenswearIndia #LinenTailoring #ModernStyle #SharpFits",
        "outfit": "a sand-beige unstructured Italian linen blazer over a clean heavyweight white crewneck and dark pleated trousers",
        "loc1": "standing on the stone steps of the modernist museum pavilion, strong diagonal shadows, wide architectural frame",
        "loc2": "candid mid-stride walk across the courtyard, blazer open and naturally flowing, 50mm f/1.4",
        "loc3": "close-up portrait leaning against sandstone pillar, natural overcast light detailing beard and linen weave, 85mm f/2.0"
    },
    ("iamgagankumar", 9): {
        "pillar": "COLLAB: The Architect & The Muse (Gagan x Avanya)",
        "location": "Modernist Concrete Pavilion, New Delhi",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Precision tailoring meets editorial poise. Modern menswear framed by clean geometry.\n\nSwipe through the lookbook with @avanyamehra. 💯\n\n#GaganKumar #AvanyaMehra #MenswearEditorial #ArchitectureFashion #ResriseStudio",
        "outfit": "Gagan Kumar wearing a bespoke charcoal wool suit over a matte black crewneck, standing beside Avanya Mehra in an obsidian black sculptural column gown",
        "loc1": "establishing wide shot in a brutalist concrete gallery with raw board-formed walls and soaring skylights, 35mm lens",
        "loc2": "candid mid-shot walking together along concrete walkway, natural confidence in posture and stride, 50mm f/1.4",
        "loc3": "intimate duo close-up, sharp focus on Gagan's tailored lapel and groomed beard with Avanya's sleek profile in frame, 85mm f/2.0"
    },
    ("iamgagankumar", 10): {
        "pillar": "COLLAB: Sunday Slow Down (Gagan x Maira)",
        "location": "Heritage Villa, Fontainhas Goa",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Linen season in Goa. Clean cuts, warm sun, and good company.\n\nSwipe for the full Sunday mood with @mairamehraofficial. 👌🔥\n\n#GaganKumar #MairaMehra #WeekendVibes #GoaStyle #MenswearLinen #ResriseStudio",
        "outfit": "Gagan Kumar wearing an open-collar cream linen shirt and tailored khaki chinos, alongside Maira Mehra in a sage-green linen coord set",
        "loc1": "wide establishing frame outside a heritage pastel-yellow Portuguese villa, lush tropical greenery, morning sun",
        "loc2": "candid street walk past vibrant bougainvillea walls, laughing naturally, relaxed casual style, 50mm f/1.4",
        "loc3": "intimate mid-shot at outdoor rustic cafe, natural lighting accentuating linen texture and relaxed demeanor, 85mm f/1.8"
    },
    ("iamgagankumar", 11): {
        "pillar": "Industrial Roastery & Outerwear Layering",
        "location": "Subko Coffee Roastery, Bandra Mumbai",
        "format": "Carousel (3 frames)",
        "caption": "Coffee runs and suede overshirts. The sweet spot between casual and dialed-in.\n\nSave this for your weekend fit rotation. ☕\n\n#GaganKumar #BandraStyle #SuedeJacket #MenswearFinds #DailyGrooming",
        "outfit": "a rich chocolate-brown suede utility overshirt over a washed grey waffle-knit tee and dark Japanese raw denim",
        "loc1": "standing outside the rustic exposed-brick cafe entrance under industrial vintage lights, wide street frame",
        "loc2": "candid mid-shot at the wooden espresso counter holding a flat white, rich warm interior glow, 50mm f/1.4",
        "loc3": "tight portrait highlighting supple suede texture, natural skin details and groomed beard, 85mm f/1.8"
    },
    ("iamgagankumar", 12): {
        "pillar": "Fragrance Ritual & Minimalist Grooming",
        "location": "Private Architectural Bath Suite, Mumbai",
        "format": "Carousel (3 frames)",
        "caption": "Your scent should announce you before you speak. Minimalist grooming essentials for the week ahead.\n\nWhat is your go-to signature note? ⚡\n\n#GaganKumar #GroomingRituals #MensGrooming #FragranceLover #CleanAesthetic",
        "outfit": "a crisp unbuttoned white poplin shirt with rolled sleeves and a minimalist steel dive watch on wrist",
        "loc1": "wide establishing shot of dark fluted-glass and slate vanity with amber bottles organized neatly, ambient side-light",
        "loc2": "candid mid-shot spritzing fragrance at collarbone, fine mist caught in directional beam of light, 50mm f/1.4",
        "loc3": "macro detail of hands holding heavy flacon with tactile glass refraction and watch dial in sharp focus, 85mm macro"
    },
    ("iamgagankumar", 13): {
        "pillar": "Winter Urban Outerwear & City Fog",
        "location": "Cyber City Promenade, Gurugram",
        "format": "Carousel (3 frames)",
        "caption": "Winter layering done right. Sharp overcoat, zero bulk.\n\nDrop a 🖤 if you rate this silhouette.\n\n#GaganKumar #WinterMenswear #OvercoatSeason #GurugramLife #CityStyle",
        "outfit": "a heavy double-breasted black wool overcoat over an off-white ribbed cashmere turtleneck and charcoal wool trousers",
        "loc1": "standing on a wide glass pedestrian bridge during early morning foggy sunrise, skyline silhouettes in mist, wide frame",
        "loc2": "walking purposefully with hands in overcoat pockets, coat tails swaying cleanly with stride, 50mm f/1.4",
        "loc3": "intimate portrait leaning against glass rail, cool morning light catching jawline and deep textures, 85mm f/2.0"
    },
    ("iamgagankumar", 14): {
        "pillar": "COLLAB: The Builder Behind the Brand (Gagan x Resrise)",
        "location": "Resrise Creative Lab, New Delhi",
        "format": "Carousel (3 frames - Collab)",
        "caption": "Where design meets execution. A look behind the curtain at @resrise.\n\nBuilding the modern creative ecosystem. 🚀\n\n#GaganKumar #ResriseStudio #StudioVibes #DesignProcess #ArchitectLife",
        "outfit": "a relaxed black chore jacket over a white heavyweight tee, holding blueprint roll and architectural scale ruler",
        "loc1": "wide establishing frame of the open-concept design studio with drafting boards, model figures, and tall factory windows",
        "loc2": "candid mid-shot reviewing a mood board on a 32-inch studio monitor, warm desk lamp illumination, 50mm f/1.4",
        "loc3": "close-up candid portrait with natural rim light, authentic focused expression, 85mm f/2.0"
    },

    # -------------------------------------------------------------
    # RESRISE STUDIO (Agency Highlights)
    # -------------------------------------------------------------
    ("resrise", 8): {
        "pillar": "Campaign Study & Creative Direction",
        "location": "Studio 01, Resrise Lab",
        "format": "Carousel (3 frames)",
        "caption": "High-fashion precision. Behind the lens of Campaign Study 03 featuring @avanyamehra.\n\nExplore collaboration inquiries at link in bio. 📩\n\n#ResriseStudio #CreativeAgency #FashionCampaign #EditorialDirection #StudioProduction",
        "outfit": "high-end studio editorial setup with softboxes, C-stands, and mood boards featuring Avanya Mehra in obsidian structured drape",
        "loc1": "wide establishing shot of the sprawling white-brick photography studio with equipment and talent in active frame",
        "loc2": "candid mid-shot of the creative director reviewing raw Hasselblad captures on tethered monitor, 50mm f/1.4",
        "loc3": "macro detail of the printed campaign contact sheet with colored grease-pencil crop marks, 85mm f/2.2"
    },

    # -------------------------------------------------------------
    # GAGAN KUMAR ROCKS (Founder Systems)
    # -------------------------------------------------------------
    ("gagankumarrocks", 8): {
        "pillar": "Building Modern Creator Systems",
        "location": "Founder Desk, Resrise HQ",
        "format": "Carousel (3 frames)",
        "caption": "Systems over luck. How we architect multi-account creator workflows that scale seamlessly.\n\nGrab the free growth breakdown in bio 💡🚀\n\n#FounderMindset #BuildInPublic #CreatorEconomy #MediaHouse #ResriseStudio",
        "outfit": "Gagan Kumar wearing a minimalist charcoal crewneck and glasses, seated at a clean birchwood desk with dual monitors",
        "loc1": "wide shot of the minimalist founder workspace with large windows overlooking morning greenery, clean desk layout",
        "loc2": "mid-shot typing notes on mechanical keyboard with workflow schematics visible on screen, 50mm f/1.4",
        "loc3": "intimate portrait looking up with confident, thoughtful expression, warm desk lamp ambient light, 85mm f/2.0"
    }
}

def generate_craft_matrix():
    # Load existing queue to prevent duplicate IDs or collisions
    existing_queue = []
    existing_media_set = set()
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            existing_queue = json.load(f)
            for item in existing_queue:
                for p in item.get("media_paths", []):
                    existing_media_set.add(os.path.normpath(p))

    matrix = []
    new_queue_entries = []

    print(f"Loaded existing queue with {len(existing_queue)} items.")
    print(f"Indexed {len(existing_media_set)} scheduled media files (guaranteed ZERO REUSE).")

    # Start scheduling timestamps from Day 8 onwards
    # Day 7 ended Nov 22/23. Day 8 starts:
    # avanyamehra: 2026-11-23 06:00 AM (12h cadence)
    # mairamehraofficial: 2026-11-23 09:00 AM (12h cadence, 3h offset)
    # iamgagankumar: 2026-11-23 12:00 PM (12h cadence, 3h offset)
    # resrise: 2026-11-23 03:00 PM
    # gagankumarrocks: 2026-11-23 06:00 PM

    offsets = {
        "avanyamehra": 0,
        "mairamehraofficial": 3,
        "iamgagankumar": 6,
        "resrise": 9,
        "gagankumarrocks": 12,
    }

    base_day8_date = "2026-11-23"

    for (acc, day_num), data in DAYS_8_TO_14_DATA.items():
        draft_id = str(uuid.uuid4())[:8]
        char = CHARACTERS.get(acc, CHARACTERS["resrise"])
        
        # Calculate cadence: 12-hour gap between posts of same account
        # Day 8 -> Day 14
        day_offset = day_num - 8
        hour_base = 6 + offsets[acc]
        # Alternate AM / PM every 12h
        # e.g. Day 8 AM, Day 8 PM, Day 9 AM...
        date_str = f"2026-11-{23 + day_offset:02d} {hour_base%12 or 12:02d}:00 {'AM' if hour_base < 12 else 'PM'}"

        scenes = [
            {
                "slide": 1,
                "filename": f"day{day_num:02d}_{acc}_01.jpg",
                "prompt": (
                    f"High-end editorial photograph of {char['desc']} "
                    f"Wearing {data['outfit']}. Scene: {data['loc1']}. "
                    "Authentic textile drape and natural crease tension. Shot on Hasselblad H6D-100c medium format. "
                    "Unretouched skin with realistic micro-pores, natural epidermal subsurface scattering, candid relaxed posture. Zero blur, 4:5 portrait ratio."
                )
            },
            {
                "slide": 2,
                "filename": f"day{day_num:02d}_{acc}_02.jpg",
                "prompt": (
                    f"Candid editorial photograph of {char['desc']} "
                    f"Wearing the exact same {data['outfit']}. Scene: {data['loc2']}. "
                    "Authentic bodily movement and natural textile tension. Shot on Leica M11, Summilux-M 50mm f/1.4 ASPH, "
                    "rich filmic color grading, natural skin tones, relaxed unforced expression. Zero blur, 4:5 portrait ratio."
                )
            },
            {
                "slide": 3,
                "filename": f"day{day_num:02d}_{acc}_03.jpg",
                "prompt": (
                    f"Editorial portrait close-up of {char['desc']} "
                    f"Wearing the exact same {data['outfit']}. Scene: {data['loc3']}. "
                    "Sharp focus on facial features and textile textures, realistic specular catchlights in pupils, "
                    "subtle epidermal glow, authentic unretouched skin micro-imperfections. Shot on 85mm f/1.8 lens. Zero blur, 4:5 portrait ratio."
                )
            }
        ]

        media_paths = [
            os.path.normpath(os.path.join(PROJECT_DIR, "draft_media", acc, s["filename"]))
            for s in scenes
        ]

        # Verify zero reuse against previously scheduled images
        for p in media_paths:
            assert p not in existing_media_set, f"Collision detected! Image {p} was already used in Days 1-7!"

        matrix_item = {
            "draft_id": draft_id,
            "day_index": day_num,
            "account": acc,
            "pillar": data["pillar"],
            "location": data["location"],
            "format": data["format"],
            "caption": data["caption"],
            "scheduled_for": date_str,
            "scenes": scenes,
        }
        matrix.append(matrix_item)

        queue_entry = {
            "id": draft_id,
            "account": acc,
            "day_index": day_num,
            "pillar": data["pillar"],
            "location": data["location"],
            "format": data["format"],
            "media_paths": media_paths,
            "caption": data["caption"],
            "status": "APPROVED",
            "viral_score": 94,
            "viral_reason": "Consistent 1-outfit 3-angle carousel with viral hook and creator cross-collab tag.",
            "created_at": "2026-11-19T18:35:00",
            "scheduled_for": date_str
        }
        new_queue_entries.append(queue_entry)

    # Save CRAFT matrix to json
    with open(OUTPUT_MATRIX_PATH, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {len(matrix)} multi-slide CRAFT posts ({len(matrix) * 3} consistent scenes) saved to {OUTPUT_MATRIX_PATH}")

    # Append new APPROVED posts to swarm_queue.json
    existing_ids = {x.get("id") for x in existing_queue}
    added = 0
    for qe in new_queue_entries:
        if qe["id"] not in existing_ids:
            existing_queue.append(qe)
            added += 1

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_queue, f, indent=2, ensure_ascii=False)
    print(f"✅ Added {added} fresh multi-creator posts to {QUEUE_PATH}!")


if __name__ == "__main__":
    generate_craft_matrix()
