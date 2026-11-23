import json

# Define character visual identities
CHARACTERS = {
    "avanyamehra": {
        "asset": "asset:AVANYA",
        "desc": "Avanya Mehra, editorial virtual muse with sharp high-fashion South Asian features, sculpted cheekbones, deep brown eyes, sleek dark hair, olive skin tone, quiet luxury editorial grace."
    },
    "mairamehraofficial": {
        "asset": "asset:MAIRA",
        "desc": "Maira Mehra, radiant Indian travel & lifestyle creator with warm golden-olive skin tone, expressive hazel-brown eyes, voluminous dark wavy hair, effortless warm smile."
    },
    "iamgagankumar": {
        "asset": "asset:GAGAN",
        "desc": "Gagan Kumar, 36-year-old North Indian architect with medium-warm brown skin tone, natural well-groomed full black beard with individual hair definition, contemplative intelligent gaze."
    }
}

# 1-Outfit, 3-Location CRAFT definitions for each of the 21 days
CRAFT_DATA = {
    # AVANYA MEHRA (7 Days)
    ("avanyamehra", 1): {
        "outfit": "a modern sculpted obsidian black structured saree with minimalist silver-thread edge detailing and a high-neck sleeveless blouse",
        "loc1": "standing in front of the marble arches of the Duomo di Milano at dawn, low-angle establishing architectural frame, 35mm lens, cool morning light",
        "loc2": "walking mid-stride through Galleria Vittorio Emanuele II under glass-vaulted ceilings, motion blur on ambient pedestrians, 50mm f/1.4",
        "loc3": "seated at a classic Milanese marble cafe table, intimate close-up profile, crisp catchlights reflecting arched windows, 85mm f/2.0"
    },
    ("avanyamehra", 2): {
        "outfit": "an oversized structured camel cashmere double-breasted trench coat over a cream silk turtleneck and tailored trousers",
        "loc1": "standing on Pont de Bir-Hakeim with steel colonnades framing the hazy Parisian skyline, wide establishing shot, soft overcast northern light",
        "loc2": "crossing a rain-dampened cobblestone street in Le Marais, coat swaying in movement, candid lifestyle framing on 50mm f/1.4",
        "loc3": "intimate portrait leaning against an ornamental Haussmannian wrought-iron balcony with classic French limestone facade, 85mm f/1.8"
    },
    ("avanyamehra", 3): {
        "outfit": "a bespoke burnt-terracotta pleated silk drape gown with architectural shoulder structure",
        "loc1": "standing within the sandstone Mughal colonnades of Humayun's Tomb, late afternoon raking golden light, wide establishing framing",
        "loc2": "walking along a gravel path lined with ancient neem trees, golden hour lens flare gently backlighting sleek dark hair, 50mm f/1.2",
        "loc3": "close-up beauty portrait leaning against red sandstone jali screen, intricate geometric shadows falling across cheekbones, 85mm f/2.2"
    },
    ("avanyamehra", 4): {
        "outfit": "a liquid metallic champagne satin slip gown with an asymmetrical draped cowl back",
        "loc1": "standing by an infinity glass ledge of a South Mumbai rooftop lounge during twilight, city skyline bokeh, establishing wide shot",
        "loc2": "candid mid-shot walking past minimalist teakwood and limestone planters, ambient evening warm cocktail illumination, 50mm f/1.4",
        "loc3": "intimate close-up holding a crystal glass, twilight blue hour sky contrasting with warm amber terrace glow, 85mm f/1.8"
    },
    ("avanyamehra", 5): {
        "outfit": "an ivory and blush pink raw Chanderi silk saree with hand-woven silver gota patti work",
        "loc1": "framed within the grand scalloped archway of a Jaipur heritage palace courtyard, early morning soft sun, establishing wide frame",
        "loc2": "walking through a bougainvillea-covered haveli garden walkway, mid-stride candid motion with authentic silk drape tension, 50mm f/1.4",
        "loc3": "tight portrait in an ornate antique mirror nook, soft diffused pink sandstone bounce filling shadows, 85mm macro detail"
    },
    ("avanyamehra", 6): {
        "outfit": "a monochrome charcoal tailored wool pant-suit with sharp lapels and a minimalist silk camisole",
        "loc1": "standing on the steps of the modern Fondazione Prada museum, brutalist architectural concrete lines, clean minimalist wide frame",
        "loc2": "walking purposefully past industrial steel and gold architectural facades in Milan, candid motion on 50mm f/1.4",
        "loc3": "close-up editorial portrait with soft directional shadow sculpting jawline, crisp eye catchlights, 85mm f/2.0"
    },
    ("avanyamehra", 7): {
        "outfit": "an ivory tailored column gown with an open sculptural back and minimal gold jewelry",
        "loc1": "standing in the Palais-Royal colonnade with black-and-white Buren columns, sunrise golden light, wide establishing frame",
        "loc2": "strolling through the Tuileries garden with autumn foliage, candid lifestyle mid-shot, warm natural backlit glow, 50mm f/1.4",
        "loc3": "close-up candid profile resting cheek near antique stone balustrade, soft romantic Parisian light rolloff, 85mm f/1.8"
    },

    # MAIRA MEHRA (7 Days)
    ("mairamehraofficial", 1): {
        "outfit": "an indigo hand-block-printed cotton anarkali with delicate white gota patti borders and silver jhumkas",
        "loc1": "standing on the marble jharokha balcony of a lakeside Udaipur palace overlooking Lake Pichola, establishing wide shot, soft dawn light",
        "loc2": "sitting on a stone courtyard bench surrounded by ornate brass planters, candid mid-shot holding a clay chai cup, 50mm f/1.4",
        "loc3": "intimate beauty portrait leaning against carved white marble pillar, warm morning sun catching hazel eyes, 85mm f/2.0"
    },
    ("mairamehraofficial", 2): {
        "outfit": "a vibrant saffron-orange organza resort saree with a sleeveless gold mirror-work blouse",
        "loc1": "standing in the lush tropical courtyard of a restored Portuguese villa in Goa, bougainvillea blooms, wide establishing frame",
        "loc2": "walking along a sun-dappled cobblestone lane in Fontainhas, candid laughter, organza fabric fluttering in sea breeze, 50mm f/1.4",
        "loc3": "close-up portrait at a rustic wooden cafe table, warm golden hour sunlight, authentic unretouched skin, 85mm f/2.0"
    },
    ("mairamehraofficial", 3): {
        "outfit": "a relaxed sage-green ribbed knit lounge set with an ecru linen duster shirt",
        "loc1": "standing on a smooth river stone beach along the turquoise Ganges in Rishikesh, foothills in background, morning mist, wide frame",
        "loc2": "sitting cross-legged on a wooden deck of a quiet wellness retreat, candid mid-shot, holding a journal, 50mm f/1.4",
        "loc3": "tight candid portrait smiling softly towards the river, diffused mountain light, authentic micro-textures, 85mm f/1.8"
    },
    ("mairamehraofficial", 4): {
        "outfit": "a cozy oat-colored chunky cable-knit sweater over dark straight-leg denim and wool scarf",
        "loc1": "standing on a cedar-wood cabin balcony in Manali with pine forests and snow-dusted peaks behind, crisp crisp mountain wide frame",
        "loc2": "walking along a sunlit mountain trail surrounded by alpine evergreens, candid mid-stride smile, 50mm f/1.4",
        "loc3": "close-up portrait clutching a steaming ceramic mug with two hands, rosy cheeks from mountain air, 85mm f/2.0"
    },
    ("mairamehraofficial", 5): {
        "outfit": "a blush pink mulmul kurta set with delicate white chikankari floral embroidery",
        "loc1": "standing in a sunny heritage courtyard in Jaipur with hand-painted fresco walls, wide establishing shot, natural morning light",
        "loc2": "sitting beside a carved sandstone fountain, candid mid-shot, smiling naturally as breeze catches hair strands, 50mm f/1.4",
        "loc3": "close-up beauty portrait showing intricate needlework on neckline and natural skin glow, 85mm f/2.2"
    },
    ("mairamehraofficial", 6): {
        "outfit": "an ivory silk tissue saree with gold zari border and delicate emerald stud earrings",
        "loc1": "standing on a teakwood balcony overlooking the hazy Arabian Sea and Marine Drive in Mumbai, sunset golden hour, wide frame",
        "loc2": "candid mid-shot at an open-air heritage rooftop restaurant, warm ambient city lights starting to twinkle, 50mm f/1.4",
        "loc3": "intimate selfie-style editorial portrait with genuine smile, hair catching golden backlight, 85mm f/1.8"
    },
    ("mairamehraofficial", 7): {
        "outfit": "a mustard-yellow chanderi silk tiered maxi dress with bohemian silver belt",
        "loc1": "standing on the Ghats of Udaipur as wooden boats glide past on the water, magic hour sunset glow, wide establishing shot",
        "loc2": "strolling along the lakeside promenade, laughing candidly towards camera, dress flowing organically, 50mm f/1.4",
        "loc3": "intimate close-up framed by traditional Rajasthani stone arches, warm amber light on face, 85mm f/2.0"
    },

    # GAGAN KUMAR (7 Days)
    ("iamgagankumar", 1): {
        "outfit": "a tailored charcoal unstructured wool-blend blazer over a matte black crewneck and slim dark trousers",
        "loc1": "standing in a brutalist concrete architectural pavilion in New Delhi with sharp geometric shadows, wide establishing frame",
        "loc2": "walking through a sunlit colonnade of a modern gallery, candid mid-stride stride, blazer in sharp focus, 50mm f/1.4",
        "loc3": "close-up portrait leaning against raw board-formed concrete, diffused northern light sculpting jawline and beard, 85mm f/2.0"
    },
    ("iamgagankumar", 2): {
        "outfit": "an olive-drab technical utility overshirt layered over a heavyweight white tee and dark Japanese selvedge denim",
        "loc1": "standing in a modern Gurugram glass-and-steel atrium, wide architectural perspective, clean industrial lines",
        "loc2": "walking past modern outdoor cafes on CyberHub promenade, holding an espresso cup, candid street photography, 50mm f/1.4",
        "loc3": "tight portrait resting near modern steel railings, natural overcast daylight, sharp beard and texture, 85mm f/1.8"
    },
    ("iamgagankumar", 3): {
        "outfit": "a crisp unbuttoned linen-cotton blend white shirt and dark tailored trousers",
        "loc1": "in a minimalist dark slate-and-fluted-glass grooming bathroom in Mumbai, wide establishing shot of architectural vanity",
        "loc2": "mid-shot examining a minimalist amber glass fragrance bottle, warm 2700K tungsten side-light, 50mm f/1.4",
        "loc3": "macro close-up of hands applying fragrance at the pulse point, sharp focus on tactile glass bottle and watch, 85mm macro"
    },
    ("iamgagankumar", 4): {
        "outfit": "a relaxed black merino wool sweater with rolled cuffs and raw canvas work trousers",
        "loc1": "wide establishing shot of a sun-drenched architectural design studio in Gurugram, concrete desks covered in blueprints and foam models",
        "loc2": "mid-shot leaning over a drafting board with a brass scale ruler, natural morning window light, candid focus, 50mm f/1.4",
        "loc3": "close-up contemplative portrait looking out the large black steel grid window, natural rim light on hair, 85mm f/2.0"
    },
    ("iamgagankumar", 5): {
        "outfit": "a dark navy unstructured Italian linen suit over a light blue open-collar poplin shirt",
        "loc1": "standing outside a modernist red-brick embassy building in New Delhi, wide geometric framing, clear morning sun",
        "loc2": "candid mid-shot walking down a tree-lined avenue, leather briefcase in hand, natural confident stride, 50mm f/1.4",
        "loc3": "editorial portrait seated on a teak outdoor bench, authentic skin texture and catchlights, 85mm f/2.0"
    },
    ("iamgagankumar", 6): {
        "outfit": "a minimalist black coach jacket layered over a heather-grey hoodie and relaxed black trousers",
        "loc1": "standing against an exposed brick and weathered steel industrial wall in Gurugram, establishing wide street shot",
        "loc2": "crossing a modern pedestrian skybridge with blurred traffic lights below, dusk blue hour, 50mm f/1.4",
        "loc3": "close-up portrait under warm streetlamp glow, authentic facial texture and natural beard definition, 85mm f/1.8"
    },
    ("iamgagankumar", 7): {
        "outfit": "a midnight-navy tailored evening jacket with a black silk-cotton knit shirt",
        "loc1": "standing at an upscale Mumbai hotel terrace lounge with Arabian Sea horizon during magic hour, establishing wide frame",
        "loc2": "sitting at a polished black granite bar counter, holding a classic tumbler, candid contemplative expression, 50mm f/1.4",
        "loc3": "intimate portrait with warm amber bar backlighting creating subtle hair separation, crisp eye focus, 85mm f/2.0"
    }
}

# Load queue
queue_path = "D:/social media/resrise-studio/swarm_queue.json"
with open(queue_path, "r", encoding="utf-8") as f:
    queue = json.load(f)

day_items = [x for x in queue if "day_index" in x]

craft_matrix = []

for item in day_items:
    d = item["day_index"]
    acc = item["account"]
    draft_id = item["id"]
    char = CHARACTERS[acc]
    craft = CRAFT_DATA[(acc, d)]
    
    # 3 CRAFT Scenes
    scenes = [
        # Frame 1: Establishing / Wide Location A
        {
            "slide": 1,
            "filename": f"day{d:02d}_{acc}_01.jpg",
            "prompt": f"High-end editorial photograph of {char['desc']} Wearing {craft['outfit']}. Scene: {craft['loc1']}. Authentic textile drape and natural crease tension. Shot on Hasselblad H6D-100c medium format, natural optical falloff. Unretouched skin with realistic micro-pores, natural epidermal subsurface scattering, candid relaxed posture."
        },
        # Frame 2: Action / In-Motion Location B
        {
            "slide": 2,
            "filename": f"day{d:02d}_{acc}_02.jpg",
            "prompt": f"Candid editorial photograph of {char['desc']} Wearing the exact same {craft['outfit']}. Scene: {craft['loc2']}. Authentic bodily movement and natural textile tension. Shot on Leica M11, Summilux-M 50mm f/1.4 ASPH, rich filmic color grading, natural skin tones, relaxed unforced expression."
        },
        # Frame 3: Intimate / Detail Location C
        {
            "slide": 3,
            "filename": f"day{d:02d}_{acc}_03.jpg",
            "prompt": f"Editorial portrait close-up of {char['desc']} Wearing the same {craft['outfit']}. Scene: {craft['loc3']}. Sharp focus on facial features and textile textures, realistic specular catchlights in pupils, subtle epidermal glow, authentic unretouched skin micro-imperfections. Shot on 85mm f/1.8 lens."
        }
    ]
    
    craft_matrix.append({
        "draft_id": draft_id,
        "day_index": d,
        "account": acc,
        "character_asset": char["asset"],
        "scenes": scenes
    })

output_path = "D:/social media/resrise-studio/craft_prompts.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(craft_matrix, f, indent=2)

print(f"Generated complete CRAFT prompts matrix for {len(craft_matrix)} days (total {len(craft_matrix)*3} scenes). Saved to {output_path}")
