#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試 OCR 推理引擎"""

import sys
import os
sys.path.insert(0, '.')

# 設定 Windows 終端機編碼
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.ocr_engine import OCREngine
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 60)
print("OCR 推理引擎測試")
print("=" * 60)
print()

# 測試圖片
test_image = r"D:\NAS_Share\Data\08_Programming_Data(程式資料)\07_DEEPSEEK_OCR\螢幕擷取畫面 2025-11-01 145249.png"

# 建立 OCR 引擎
print("【步驟 1】初始化 OCR 引擎")
engine = OCREngine(
    model_path="./models/deepseek-ocr",
    device="cuda"
)
print("✓ OCR 引擎初始化完成")
print()

# 載入模型
print("【步驟 2】載入模型")
engine.load_model()
print()

# 取得模型資訊
print("【步驟 3】模型資訊")
model_info = engine.get_model_info()
print(f"  模型已載入: {model_info['loaded']}")
print(f"  參數量: {model_info['parameters']:.2f}B")
if 'vram_used_gb' in model_info:
    print(f"  VRAM 使用: {model_info['vram_used_gb']:.2f} GB / {model_info['vram_total_gb']:.2f} GB")
print()

# 處理圖片
print("【步驟 4】處理圖片")
print(f"  圖片: {test_image}")
print()

result = engine.process_image(
    test_image,
    base_size=1024,
    image_size=1024,
    crop_mode=False,
    output_path="outputs/engine_test",
    save_results=True
)

print()
print("=" * 60)
print("OCR 結果")
print("=" * 60)
print(f"成功: {result.success}")
print(f"處理時間: {result.processing_time:.2f} 秒")
print(f"圖片尺寸: {result.image_size}")
print(f"VRAM 使用: {result.vram_used_gb:.2f} GB")
print(f"時間戳: {result.timestamp}")
print()

if result.success:
    print("辨識文字:")
    print("-" * 60)
    # 從輸出檔案讀取結果
    try:
        with open("outputs/engine_test/result.mmd", "r", encoding="utf-8") as f:
            content = f.read()
        print(content)
    except:
        print("(無法讀取輸出檔案)")
    print("-" * 60)
else:
    print(f"錯誤: {result.error_message}")

print()
print("=" * 60)
print("✓ 測試完成！")
print("=" * 60)
