"""
prepare_instagram_media.py
Utility to format Google Flow 3:4 portrait downloads (1792x2400) for Instagram:
1. Slices off the bottom 220px margin where Google Flow's AI star watermark is located (y >= 2180).
2. Crops width symmetrically (24px left, 24px right) to achieve an EXACT 4:5 aspect ratio (1744 x 2180 = 0.8000).
3. Resizes to Instagram's standard crisp 1080x1350 resolution.
4. Result: 100% PRISTINE texture, ZERO watermarks, ZERO inpainting blur, EXACT 4:5 portrait.
"""

import os
import cv2
import numpy as np

def crop_to_instagram_4_5(image_path: str, output_path: str = None, target_width: int = 1080, target_height: int = 1350) -> np.ndarray:
    """
    Crops a Google Flow 3:4 portrait (e.g. 1792x2400) to exact Instagram 4:5 (1080x1350).
    Slices away the bottom 220px to permanently eliminate the Google AI star watermark without any inpainting blur.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image at {image_path}")
        
    h, w, _ = img.shape
    
    # In 2K renders from Google Flow (1792 x 2400):
    # Star watermark is located in y in [2200:2360], x in [1600:1750]
    # Slicing y at max 2180 completely eliminates the star.
    if h == 2400 and w == 1792:
        # Crop y: 0 to 2180 (height = 2180)
        # To get exact 4:5 (0.8), target width = 2180 * 0.8 = 1744
        # Crop 24px from left and right
        cropped = img[0:2180, 24:1768]
    else:
        # General formula for other sizes:
        # Slice bottom 10% to eliminate watermark, then adjust width to 4:5
        new_h = int(h * 0.908) # leaves 0 to 0.908
        target_w = int(new_h * 0.8)
        left_offset = max(0, (w - target_w) // 2)
        cropped = img[0:new_h, left_offset:left_offset + target_w]
        
    # Resize to exact Instagram target resolution (1080x1350)
    resized = cv2.resize(cropped, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
    
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cv2.imwrite(output_path, resized, [cv2.IMWRITE_JPEG_QUALITY, 98])
        
    return resized

def process_image_for_instagram(input_path: str, output_path: str) -> str:
    """
    Processes Google Flow 3:4 portrait to exact Instagram 4:5 without watermark.
    """
    crop_to_instagram_4_5(input_path, output_path=output_path, target_width=1080, target_height=1350)
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        inp = sys.argv[1]
        out = sys.argv[2]
        process_image_for_instagram(inp, out)
        print(f"Processed: {out}")
