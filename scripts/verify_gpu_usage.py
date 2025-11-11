#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證 GPU 使用腳本
確認模型是否真的在 GPU 上運行
"""

import sys
import os
from pathlib import Path

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

import torch
from src import OCREngine

print("=" * 60)
print("GPU 使用驗證")
print("=" * 60)
print()

# 1. 檢查 CUDA
print("【步驟 1】檢查 CUDA 可用性")
print(f"CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU 名稱: {torch.cuda.get_device_name(0)}")
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"初始 VRAM: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
else:
    print("❌ CUDA 不可用！")
    sys.exit(1)

print()

# 2. 初始化 OCR 引擎
print("【步驟 2】初始化 OCR 引擎")
engine = OCREngine(model_path="./models/deepseek-ocr", device="cuda")
print(f"引擎裝置設定: {engine.device}")
print()

# 3. 載入模型
print("【步驟 3】載入模型")
print("載入中...")
engine.load_model()
print()

# 4. 檢查 VRAM
print("【步驟 4】檢查 VRAM 使用")
vram_used = torch.cuda.memory_allocated(0) / 1024**3
vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
vram_percent = (vram_used / vram_total) * 100

print(f"VRAM 使用: {vram_used:.2f} GB / {vram_total:.2f} GB ({vram_percent:.1f}%)")
print()

# 5. 判斷結果
print("【步驟 5】驗證結果")
print("=" * 60)

if vram_used > 1.0:  # 模型至少應該佔用 1GB
    print("✅ 成功！模型已載入到 GPU")
    print(f"   VRAM 使用: {vram_used:.2f} GB")
    print("   模型將使用 GPU 進行推理")
else:
    print("❌ 失敗！模型可能在 CPU 上")
    print(f"   VRAM 使用過低: {vram_used:.2f} GB")
    print("   請檢查代碼")

print("=" * 60)
print()

# 6. 顯示模型資訊
print("【模型資訊】")
model_info = engine.get_model_info()
for key, value in model_info.items():
    print(f"  {key}: {value}")

print()
print("驗證完成！")
