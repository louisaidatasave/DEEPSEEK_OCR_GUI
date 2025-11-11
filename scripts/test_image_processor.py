#!/usr/bin/env python3
"""測試圖片預處理模組"""

import sys
sys.path.insert(0, '.')

from src.image_processor import ImageProcessor, load_image, get_image_info
from pathlib import Path

print("=" * 60)
print("圖片預處理模組測試")
print("=" * 60)
print()

# 測試圖片
test_images = [
    r"D:\NAS_Share\Data\08_Programming_Data(程式資料)\07_DEEPSEEK_OCR\螢幕擷取畫面 2025-11-01 145249.png",
    r"D:\NAS_Share\Data\08_Programming_Data(程式資料)\07_DEEPSEEK_OCR\螢幕擷取畫面 2025-11-01 150006.png"
]

# 測試 1: 取得圖片資訊
print("【測試 1】取得圖片資訊")
for img_path in test_images:
    try:
        info = get_image_info(img_path)
        print(f"\n圖片: {info['file_name']}")
        print(f"  尺寸: {info['width']} x {info['height']} px")
        print(f"  格式: {info['format']}")
        print(f"  模式: {info['mode']}")
        print(f"  檔案大小: {info['file_size_mb']:.2f} MB")
    except Exception as e:
        print(f"✗ 錯誤: {e}")

print()
print("=" * 60)

# 測試 2: 載入圖片（不調整大小）
print("【測試 2】載入圖片（原始大小）")
processor = ImageProcessor()

for img_path in test_images:
    try:
        image, info = processor.process_image(img_path)
        print(f"\n✓ {info['file_name']}")
        print(f"  原始尺寸: {info['original_size']}")
        print(f"  處理後尺寸: {info['processed_size']}")
        print(f"  是否調整: {info['resized']}")
    except Exception as e:
        print(f"✗ 錯誤: {e}")

print()
print("=" * 60)

# 測試 3: 載入圖片並調整大小
print("【測試 3】載入圖片並調整大小（最大 1024px）")
processor = ImageProcessor(max_size=1024)

for img_path in test_images:
    try:
        image, info = processor.process_image(img_path)
        print(f"\n✓ {info['file_name']}")
        print(f"  原始尺寸: {info['original_size']}")
        print(f"  處理後尺寸: {info['processed_size']}")
        print(f"  是否調整: {info['resized']}")
    except Exception as e:
        print(f"✗ 錯誤: {e}")

print()
print("=" * 60)

# 測試 4: 使用便利函數
print("【測試 4】使用便利函數")
try:
    image = load_image(test_images[0], max_size=512)
    print(f"✓ 成功載入圖片，尺寸: {image.size}")
except Exception as e:
    print(f"✗ 錯誤: {e}")

print()
print("=" * 60)
print("✓ 所有測試完成！")
print("=" * 60)
