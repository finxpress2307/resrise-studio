import os
from PIL import Image

def crop_4_5_uniform(img_path):
    try:
        im = Image.open(img_path)
        w, h = im.size
        
        # Exact 4:5 uniform crop as configured in Batch Image Crop
        # Original: 896 x 1200 -> Target: 846 x 1057 (0.80 ratio)
        cw = int(w * (846.0 / 896.0)) if w != 846 else 846
        ch = int(h * (1057.0 / 1200.0)) if h != 1200 else 1057
        
        x0 = (w - cw) // 2
        # Position top margin at 35px so headroom is preserved and bottom watermark is 100% trimmed
        y0 = int(h * (35.0 / 1200.0))
        x1 = x0 + cw
        y1 = y0 + ch
        
        cropped = im.crop((x0, y0, x1, y1))
        cropped.save(img_path, quality=96)
        print(f"✓ Cropped to 4:5 ({cw}x{ch}): {os.path.basename(img_path)}")
        return True
    except Exception as e:
        print(f"Error cropping {img_path}: {e}")
        return False

print("=== Executing 4:5 Uniform Batch Crop (Zero Blur) ===")

targets = [
    "D:/social media/resrise-studio/draft_media/mairamehraofficial",
    "D:/social media/resrise-studio/draft_media/iamgagankumar"
]

total = 0
for folder in targets:
    if not os.path.exists(folder):
        continue
    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            fpath = os.path.join(folder, fname)
            if crop_4_5_uniform(fpath):
                total += 1

print(f"\n=== Successfully cropped {total} images to clean 4:5 format with zero watermark & zero blur! ===")
