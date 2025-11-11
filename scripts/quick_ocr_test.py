#!/usr/bin/env python3
"""
快速 OCR 測試腳本
測試 DeepSeek-OCR 將圖片轉換為 Markdown
"""

import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import time

print("=" * 60)
print("DeepSeek-OCR 快速測試")
print("=" * 60)
print()

# 測試圖片路徑
image_path = r"D:\NAS_Share\Data\08_Programming_Data(程式資料)\07_DEEPSEEK_OCR\螢幕擷取畫面 2025-11-01 145249.png"

print(f"測試圖片: {image_path}")
print()

# 載入圖片
print("【步驟 1】載入圖片...")
try:
    image = Image.open(image_path).convert("RGB")
    print(f"✓ 圖片載入成功")
    print(f"  尺寸: {image.size[0]} x {image.size[1]} px")
    print(f"  格式: {image.format if hasattr(image, 'format') else 'PNG'}")
except Exception as e:
    print(f"✗ 圖片載入失敗: {e}")
    exit(1)

print()

# 載入模型
print("【步驟 2】載入模型...")
try:
    model_path = "./models/deepseek-ocr"
    
    print("  載入 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )
    
    print("  載入模型...")
    model = AutoModel.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="cuda"
    )
    model = model.eval()
    
    print(f"✓ 模型載入成功")
    
    # 顯示 VRAM 使用
    if torch.cuda.is_available():
        vram_used = torch.cuda.memory_allocated(0) / 1024**3
        print(f"  VRAM 使用: {vram_used:.2f} GB")
    
except Exception as e:
    print(f"✗ 模型載入失敗: {e}")
    exit(1)

print()

# 執行 OCR
print("【步驟 3】執行 OCR...")
print("  提示詞: <image>\\n<|grounding|>Convert the document to markdown.")
print("  模式: Base (1024x1024)")
print("  處理中... (這可能需要 10-30 秒)")
print()

try:
    # 使用官方推薦的提示詞
    prompt = "<image>\n<|grounding|>Convert the document to markdown. "
    
    # 記錄開始時間
    start_time = time.time()
    
    # 使用模型的 infer 方法（官方方式）
    # Base 模式: base_size = 1024, image_size = 1024, crop_mode = False
    result = model.infer(
        tokenizer,
        prompt=prompt,
        image_file=image_path,
        output_path="outputs",
        base_size=1024,
        image_size=1024,
        crop_mode=False,
        save_results=True,
        test_compress=True
    )
    
    # 記錄結束時間
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"✓ OCR 完成！")
    print(f"  處理時間: {processing_time:.2f} 秒")
    
    # 顯示 VRAM 使用
    if torch.cuda.is_available():
        vram_used = torch.cuda.memory_allocated(0) / 1024**3
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"  VRAM 使用: {vram_used:.2f} GB / {vram_total:.2f} GB ({vram_used/vram_total*100:.1f}%)")
    
    print()
    print("=" * 60)
    print("OCR 結果（Markdown 格式）")
    print("=" * 60)
    print()
    print(result)
    print()
    print("=" * 60)
    
    # 儲存結果
    output_file = "outputs/ocr_result.md"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n✓ 結果已儲存至: {output_file}")
    except Exception as e:
        print(f"\n⚠ 無法儲存結果: {e}")
    
    print()
    print("🎉 測試成功！")
    
except Exception as e:
    print(f"✗ OCR 執行失敗: {e}")
    print()
    print("詳細錯誤:")
    import traceback
    traceback.print_exc()
    exit(1)
