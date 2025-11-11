#!/usr/bin/env python3
"""
測試 DeepSeek-OCR 模型載入
使用正確的 transformers 版本 (4.46.3)
"""

import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import sys

print("=" * 60)
print("DeepSeek-OCR 模型載入測試")
print("=" * 60)
print()

# 檢查環境
print("【環境檢查】")
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# 檢查 transformers 版本
import transformers
print(f"transformers 版本: {transformers.__version__}")

# 檢查 Flash Attention
try:
    import flash_attn
    print(f"Flash Attention: {flash_attn.__version__}")
except ImportError:
    print("Flash Attention: 未安裝（將使用標準模式）")

print()
print("【載入模型】")
print("模型路徑: ./models/deepseek-ocr")
print("正在載入... (這可能需要 1-2 分鐘)")
print()

try:
    # 載入 tokenizer
    print("  [1/3] 載入 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        "./models/deepseek-ocr",
        trust_remote_code=True
    )
    print(f"  ✓ Tokenizer 載入成功 (詞彙量: {len(tokenizer)})")
    
    # 載入模型
    print("  [2/3] 載入模型...")
    model = AutoModel.from_pretrained(
        "./models/deepseek-ocr",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="cuda"
    )
    print(f"  ✓ 模型載入成功")
    
    # 設定為評估模式
    print("  [3/3] 設定評估模式...")
    model = model.eval()
    print(f"  ✓ 模型已準備就緒")
    
    print()
    print("=" * 60)
    print("✓ 模型載入測試通過！")
    print("=" * 60)
    print()
    print("模型資訊:")
    print(f"  - 裝置: {next(model.parameters()).device}")
    print(f"  - 資料類型: {next(model.parameters()).dtype}")
    print(f"  - 參數量: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B")
    
    # 檢查 VRAM 使用
    if torch.cuda.is_available():
        vram_used = torch.cuda.memory_allocated(0) / 1024**3
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"  - VRAM 使用: {vram_used:.2f} GB / {vram_total:.2f} GB ({vram_used/vram_total*100:.1f}%)")
    
    print()
    print("🎉 恭喜！模型已成功載入，可以開始 OCR 測試了！")
    print()
    print("下一步：執行 'python scripts/test_ocr.py' 進行實際 OCR 測試")
    
    sys.exit(0)
    
except Exception as e:
    print()
    print("=" * 60)
    print("✗ 模型載入失敗")
    print("=" * 60)
    print(f"錯誤訊息: {e}")
    print()
    print("可能的解決方案:")
    print("1. 確認 transformers 版本為 4.46.3")
    print("2. 確認模型檔案完整")
    print("3. 檢查 VRAM 是否足夠")
    
    import traceback
    print()
    print("詳細錯誤:")
    traceback.print_exc()
    
    sys.exit(1)
