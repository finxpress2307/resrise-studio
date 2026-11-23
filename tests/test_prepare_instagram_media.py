"""
tests/test_prepare_instagram_media.py
Tests for watermark-free Instagram 4:5 portrait cropping.
"""

import os
import pytest
import numpy as np
import cv2
from scripts.prepare_instagram_media import crop_to_instagram_4_5, process_image_for_instagram

@pytest.fixture
def sample_3_4_image(tmp_path):
    # Create synthetic 3:4 portrait (1792x2400)
    img = np.ones((2400, 1792, 3), dtype=np.uint8) * 120
    # Add a mock watermark pattern in the bottom right corner (y=2300, x=1650)
    img[2250:2350, 1600:1700] = 255
    path = str(tmp_path / "sample_3_4.jpg")
    cv2.imwrite(path, img)
    return path

def test_crop_to_instagram_4_5_dimensions_and_removes_bottom(sample_3_4_image, tmp_path):
    out = str(tmp_path / "cropped.jpg")
    result = crop_to_instagram_4_5(sample_3_4_image, output_path=out, target_width=1080, target_height=1350)
    assert os.path.exists(out)
    assert result.shape == (1350, 1080, 3)
    assert round(result.shape[1] / result.shape[0], 2) == 0.80

def test_process_image_for_instagram_full_flow(sample_3_4_image, tmp_path):
    out = str(tmp_path / "final_ig.jpg")
    res_path = process_image_for_instagram(sample_3_4_image, out)
    assert res_path == out
    assert os.path.exists(out)
    final_img = cv2.imread(out)
    assert final_img.shape == (1350, 1080, 3)
