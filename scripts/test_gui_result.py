#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 GUI 結果顯示
驗證 OCR 結果是否正確顯示
"""

import sys
import os
from pathlib import Path

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

from src import OCREngine

print("=" * 60)
print("測試 OCR 結果讀取")
print("=" * 60)
print()

# 尋找測試圖片
test_images = list(Path(".").glob("*.png")) + list(Path(".").glob("*.jpg"))
if not test_images:
    print("找不到測試圖片，請在專案根目錄放置圖片檔案")
    sys.exit(1)

test_image = test_images[0]
print(f"使用測試圖片: {test_image.name}")
print()

# 初始化 OCR 引擎
print("初始化 OCR 引擎...")
engine = OCREngine(model_path="./models/deepseek-ocr")
engine.load_model()
print()

# 處理圖片
print("處理圖片...")
result = engine.process_image(
    test_image,
    output_path="outputs/test_result",
    save_results=True
)
print()

# 檢查結果
print("=" * 60)
print("結果檢查")
print("=" * 60)
print()

print(f"處理狀態: {'成功' if result.success else '失敗'}")
print(f"處理時間: {result.processing_time:.2f} 秒")
print(f"VRAM 使用: {result.vram_used_gb:.2f} GB")
print()

if result.text_content:
    print("✅ 結果內容已取得")
    print(f"   字元數: {len(result.text_content)}")
    print(f"   行數: {result.text_content.count(chr(10)) + 1}")
    print()
    print("前 200 字元預覽:")
    print("-" * 60)
    print(result.text_content[:200])
    if len(result.text_content) > 200:
        print("...")
    print("-" * 60)
else:
    print("❌ 結果內容為空")
    print("   這是問題所在！")

print()
print("=" * 60)
print("測試完成")
print("=" * 60)
