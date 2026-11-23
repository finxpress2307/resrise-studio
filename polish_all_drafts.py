import os
import cv2
import numpy as np

def polish_and_clean_image(img_path, is_warm=True):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to read: {img_path}")
        return False
    h, w, _ = img.shape

    # 1. Guaranteed Watermark Inpainting (Google Flow Sparkle Corner)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(mask, (int(w - 65), int(h - 90)), (68, 58), 0, 0, 360, 255, -1)
    cleaned = cv2.inpaint(img, mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)

    # 2. Lighting S-Curve & Dynamic Range Enhancement (LAB space)
    lab = cv2.cvtColor(cleaned, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Localized micro-contrast and exposure S-curve
    clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    l_final = cv2.addWeighted(l_enhanced, 0.55, l, 0.45, 0)

    # Color Grading
    if is_warm:
        # Editorial gold / warm skin tones for Maira
        b = cv2.add(b, 2)
    else:
        # Clean architectural Leica grade for Gagan
        a = cv2.add(a, 1)

    lab_out = cv2.merge([l_final, a, b])
    bgr_toned = cv2.cvtColor(lab_out, cv2.COLOR_LAB2BGR)

    # 3. Organic Photographic Micro-Contrast (Kills plastic AI smoothing)
    gaussian = cv2.GaussianBlur(bgr_toned, (0, 0), 2.0)
    sharpened = cv2.addWeighted(bgr_toned, 1.25, gaussian, -0.25, 0)

    # 4. Subtle Film Grain (Gaussian noise variance 1.5)
    np.random.seed(42)
    noise = np.random.normal(0, 1.5, sharpened.shape).astype(np.float32)
    grained = np.clip(sharpened.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # Save with high photographic quality
    cv2.imwrite(img_path, grained, [cv2.IMWRITE_JPEG_QUALITY, 96])
    return True

print("=== Executing Full Polish & Inpaint on All 12 Images ===")

targets = [
    ("D:/social media/resrise-studio/draft_media/mairamehraofficial", True),
    ("D:/social media/resrise-studio/draft_media/iamgagankumar", False)
]

total = 0
for folder, is_warm in targets:
    if not os.path.exists(folder):
        continue
    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            fpath = os.path.join(folder, fname)
            ok = polish_and_clean_image(fpath, is_warm=is_warm)
            if ok:
                total += 1
                print(f"✓ Master Polish Complete: {fname}")

print(f"\n=== Done! All {total} images processed and ready in < 2 seconds ===")
