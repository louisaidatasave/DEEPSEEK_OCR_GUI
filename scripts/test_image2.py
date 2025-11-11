#!/usr/bin/env python3
"""測試第二張圖片"""

import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import time

print("=" * 60)
print("DeepSeek-OCR 測試 - 圖片 2")
print("=" * 60)
print()

# 測試圖片路徑
image_path = r"D:\NAS_Share\Data\08_Programming_Data(程式資料)\07_DEEPSEEK_OCR\螢幕擷取畫面 2025-11-01 150006.png"

print(f"測試圖片: {image_path}")
print()

# 載入圖片
print("【步驟 1】載入圖片...")
try:
    image = Image.open(image_path).convert("RGB")
    print(f"✓ 圖片載入成功")
    print(f"  尺寸: {image.size[0]} x {image.size[1]} px")
except Exception as e:
    print(f"✗ 圖片載入失敗: {e}")
    exit(1)

print()

# 載入模型
print("【步驟 2】載入模型...")
try:
    model_path = "./models/deepseek-ocr"
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="cuda"
    )
    model = model.eval()
    
    print(f"✓ 模型載入成功")
    
except Exception as e:
    print(f"✗ 模型載入失敗: {e}")
    exit(1)

print()

# 執行 OCR
print("【步驟 3】執行 OCR...")
print("  處理中...")
print()

try:
    prompt = "<image>\n<|grounding|>Convert the document to markdown. "
    
    start_time = time.time()
    
    result = model.infer(
        tokenizer,
        prompt=prompt,
        image_file=image_path,
        output_path="outputs/test2",
        base_size=1024,
        image_size=1024,
        crop_mode=False,
        save_results=True,
        test_compress=True
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"✓ OCR 完成！")
    print(f"  處理時間: {processing_time:.2f} 秒")
    
    if torch.cuda.is_available():
        vram_used = torch.cuda.memory_allocated(0) / 1024**3
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"  VRAM 使用: {vram_used:.2f} GB / {vram_total:.2f} GB")
    
    print()
    print("=" * 60)
    print("✓ 測試完成！")
    print("=" * 60)
    print()
    print("結果已儲存至: outputs/test2/")
    print("  - result.mmd (Markdown 格式)")
    print("  - result_with_boxes.jpg (帶標註)")
    
except Exception as e:
    print(f"✗ OCR 執行失敗: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
