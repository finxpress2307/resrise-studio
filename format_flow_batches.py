import json
import os

PROJECT_DIR = r"D:\social media\resrise-studio"
JSON_PATH = os.path.join(PROJECT_DIR, "craft_prompts_days08_14.json")
TXT_OUTPUT_PATH = os.path.join(PROJECT_DIR, "GOOGLE_FLOW_PROMPTS_DAYS08_14.txt")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    matrix = json.load(f)

lines = []
lines.append("================================================================================")
lines.append("       GOOGLE FLOW - RESRISE STUDIO BATCH GENERATION (DAYS 8-14)")
lines.append("================================================================================")
lines.append("INSTRUCTIONS FOR GOOGLE FLOW:")
lines.append("Copy and paste each batch below directly into the 'What do you want to create?'")
lines.append("input box in your Google Flow project.\n")

# Group into clean batches
# Batch 1: AVANYA MEHRA (Solo Days 8, 10, 12, 13)
# Batch 2: MAIRA MEHRA (Solo Days 8, 9, 12, 13, 14)
# Batch 3: GAGAN KUMAR (Solo Days 8, 11, 12, 13)
# Batch 4: CREATOR COLLABORATIONS (Days 9, 10, 11, 14 - Multi-Character Collabs)
# Batch 5: AGENCY & FOUNDER (Resrise & Gagan Rocks)

batches = {
    "BATCH 1: AVANYA MEHRA (High-Fashion Solo Days)": [
        m for m in matrix if m["account"] == "avanyamehra" and "COLLAB" not in m["pillar"]
    ],
    "BATCH 2: MAIRA MEHRA (Travel & Saree Solo Days)": [
        m for m in matrix if m["account"] == "mairamehraofficial" and "COLLAB" not in m["pillar"]
    ],
    "BATCH 3: GAGAN KUMAR (Menswear & Grooming Solo Days)": [
        m for m in matrix if m["account"] == "iamgagankumar" and "COLLAB" not in m["pillar"]
    ],
    "BATCH 4: MULTI-CREATOR COLLABORATIONS (Duo Collabs)": [
        m for m in matrix if "COLLAB" in m["pillar"]
    ],
    "BATCH 5: AGENCY & FOUNDER (Resrise Studio & Founder Systems)": [
        m for m in matrix if m["account"] in ("resrise", "gagankumarrocks")
    ]
}

asset_map = {
    "avanyamehra": "character asset:AVANYA locked",
    "mairamehraofficial": "character asset:MAIRA locked",
    "iamgagankumar": "character asset:GAGAN locked",
    "resrise": "character asset:AVANYA locked",
    "gagankumarrocks": "character asset:GAGAN locked"
}

for batch_title, items in batches.items():
    if not items:
        continue
    lines.append("--------------------------------------------------------------------------------")
    lines.append(batch_title)
    lines.append("--------------------------------------------------------------------------------\n")
    
    prompt_text = "Generate the following high-fashion editorial carousel scenes in 3:4 portrait aspect ratio.\n"
    prompt_text += "CRITICAL RULE: For each day, maintain 100% IDENTICAL attire, dress, fabrics, and styling across all 3 slides.\n\n"
    
    count = 1
    for m in items:
        acc = m["account"]
        day = m["day_index"]
        pillar = m["pillar"]
        loc = m["location"]
        
        # Determine asset tags
        if "Avanya x Gagan" in pillar:
            char_tag = "character asset:AVANYA and character asset:GAGAN locked"
        elif "Avanya x Maira" in pillar or "Maira x Avanya" in pillar:
            char_tag = "character asset:AVANYA and character asset:MAIRA locked"
        elif "Maira x Gagan" in pillar or "Gagan x Maira" in pillar:
            char_tag = "character asset:MAIRA and character asset:GAGAN locked"
        else:
            char_tag = asset_map.get(acc, "character asset:AVANYA locked")
            
        prompt_text += f"[DAY {day:02d} - {pillar} | Location: {loc} | Tag: {char_tag}]\n"
        for s in m["scenes"]:
            slide_num = s["slide"]
            filename = s["filename"]
            # Clean prompt for Flow
            scene_prompt = s["prompt"].replace("Zero blur, 4:5 portrait ratio.", "").strip()
            prompt_text += f"  Slide {slide_num} ({filename}): {scene_prompt} ({char_tag})\n"
        prompt_text += "\n"
        count += 1
        
    lines.append(prompt_text)

with open(TXT_OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ Generated Google Flow prompt instructions saved to {TXT_OUTPUT_PATH}")
